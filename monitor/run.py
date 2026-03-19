"""
Entry point for running the dependency monitor crew.
Can be called from Django management command or standalone.
"""

import io
import json
import logging
import os
import re
import sys
import threading
import time
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

_stdout_lock = threading.Lock()

# Noise patterns to filter from stdout capture
_NOISE_PATTERNS = [
    "verbose_output",
    "DEBUG",
    "httpx",
    "httpcore",
    "litellm",
    "WARNING",
    "retry",
]


class _LogCapture:
    """Captures stdout and forwards interesting lines to log_callback."""

    def __init__(self, original, log_callback):
        self._original = original
        self._callback = log_callback
        self._buffer = ""

    def write(self, text):
        try:
            self._original.write(text)
        except UnicodeEncodeError:
            self._original.write(text.encode("utf-8", errors="replace").decode("ascii", errors="replace"))
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if not line or len(line) < 10:
                continue
            # Filter noise
            if any(p in line for p in _NOISE_PATTERNS):
                continue
            # Detect agent activity from CrewAI verbose output
            if "Agent:" in line or "Working Agent:" in line:
                self._callback("agent", "", line)
            elif "Tool:" in line or "Using tool:" in line:
                self._callback("tool", "", line[:300])
            elif "Thought:" in line:
                self._callback("thought", "", line[:300])
            elif any(kw in line.lower() for kw in ["final answer", "finished"]):
                self._callback("result", "", line[:400])

    def flush(self):
        self._original.flush()


def _poll_token_usage(agents, job_pk, stop_event):
    """Background thread that polls agent LLM token usage every 2 seconds."""
    try:
        import django
        django.setup()
        from dashboard.models import ScanJob
    except Exception:
        return

    while not stop_event.is_set():
        stop_event.wait(2)
        if stop_event.is_set():
            break
        try:
            total = 0
            for agent in agents:
                llm = getattr(agent, "llm", None)
                if not llm:
                    continue
                # CrewAI LLM wraps litellm; try common token tracking attributes
                usage = getattr(llm, "_token_usage", None) or getattr(llm, "token_usage", None)
                if usage:
                    total += getattr(usage, "total_tokens", 0) or 0
                    total += getattr(usage, "prompt_tokens", 0) or 0
                    total += getattr(usage, "completion_tokens", 0) or 0
            if total > 0:
                ScanJob.objects.filter(pk=job_pk).update(token_count=total)
        except Exception:
            logger.error("Error polling token usage", exc_info=True)


def run_crew(requirements_path: str | None = None, log_callback=None, job_pk: int | None = None) -> dict:
    """
    Run the CrewAI crew and return structured results.

    Args:
        requirements_path: Path to requirements.txt to scan
        log_callback: Callable(event_type, agent_name, message) for log entries
        job_pk: Optional ScanJob primary key for live progress updates

    Returns a dict with:
        - status: "critical" | "warning" | "ok"
        - findings: list of finding dicts
        - tip_of_the_week: str
        - quote_of_the_week: str
        - total_tokens: int
        - estimated_cost: Decimal
        - raw_output: str
        - total_dependencies: int
        - outdated_count: int
        - vulnerability_count: int
    """
    from .crew import AGENT_SEQUENCE, create_crew

    if not requirements_path:
        requirements_path = os.environ.get(
            "MONITORED_PROJECT_PATH",
            str(Path(__file__).parent.parent.parent / "django-finance-project_2"),
        )
        requirements_path = str(Path(requirements_path) / "requirements.txt")

    print(f"[Monitor] Scanning: {requirements_path}")

    # Track which task we're on (mutable container for closure)
    task_index = [0]

    def _update_job(**fields):
        """Helper to update ScanJob fields if job_pk is set."""
        if job_pk:
            try:
                from dashboard.models import ScanJob
                ScanJob.objects.filter(pk=job_pk).update(**fields)
            except Exception:
                logger.warning("Error updating job", exc_info=True)

    # Build CrewAI callbacks that feed our log_callback
    step_cb = None
    task_cb = None
    if log_callback:
        def step_cb(step_output):
            try:
                # CrewAI step_output can be AgentAction or AgentFinish
                # AgentAction has: tool, tool_input, log/thought
                # AgentFinish has: output, log
                tool = getattr(step_output, "tool", "")
                tool_input = getattr(step_output, "tool_input", "")
                output = getattr(step_output, "output", "")
                thought = getattr(step_output, "thought", "") or getattr(step_output, "log", "")

                # Determine current agent name from sequence
                idx = min(task_index[0], len(AGENT_SEQUENCE) - 1)
                agent_name = AGENT_SEQUENCE[idx]

                if tool:
                    input_str = str(tool_input)[:150] if tool_input else ""
                    log_callback("tool", agent_name, f"Tool: {tool}" + (f" ({input_str}...)" if input_str else ""))
                elif thought and not output:
                    short = str(thought)[:300] + ("..." if len(str(thought)) > 300 else "")
                    log_callback("thought", agent_name, short)
                elif output:
                    short = str(output)[:400] + ("..." if len(str(output)) > 400 else "")
                    log_callback("result", agent_name, short)
            except Exception:
                logger.error("Error in step_cb", exc_info=True)

        def task_cb(task_output):
            try:
                idx = task_index[0]
                agent_name = AGENT_SEQUENCE[idx] if idx < len(AGENT_SEQUENCE) else "Agent"
                summary = str(getattr(task_output, "raw", ""))[:300]

                log_callback("task_done", agent_name, f"Taak afgerond\n{summary}")

                # Advance to next agent
                task_index[0] = idx + 1
                next_idx = task_index[0]
                tasks_done = next_idx

                if next_idx < len(AGENT_SEQUENCE):
                    next_agent = AGENT_SEQUENCE[next_idx]
                    log_callback("agent", next_agent, f"Agent {next_idx + 1}/{len(AGENT_SEQUENCE)} gestart")
                    _update_job(
                        active_agent=next_agent,
                        tasks_completed=tasks_done,
                        progress_message=f"Agent {next_idx + 1}/{len(AGENT_SEQUENCE)}: {next_agent}",
                    )
                else:
                    _update_job(tasks_completed=tasks_done)
            except Exception:
                logger.error("Error in task_cb", exc_info=True)

    crew, agents = create_crew(requirements_path, step_callback=step_cb, task_callback=task_cb)

    if log_callback:
        first_agent = AGENT_SEQUENCE[0]
        log_callback("start", "Crew", "CrewAI gestart — agents worden uitgevoerd...")
        log_callback("agent", first_agent, f"Agent 1/{len(AGENT_SEQUENCE)} gestart")
        _update_job(
            active_agent=first_agent,
            tasks_completed=0,
            progress_message=f"Agent 1/{len(AGENT_SEQUENCE)}: {first_agent}",
        )

    # Start token polling thread
    stop_polling = threading.Event()
    poll_thread = None
    if job_pk:
        poll_thread = threading.Thread(
            target=_poll_token_usage, args=(agents, job_pk, stop_polling), daemon=True
        )
        poll_thread.start()

    # Force UTF-8 stdout to avoid 'charmap' codec errors on Windows
    # Use lock to prevent concurrent threads from corrupting stdout
    with _stdout_lock:
        original_stdout = sys.stdout
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
            )
        except AttributeError:
            pass  # stdout has no buffer (e.g. some test environments)

        if log_callback:
            sys.stdout = _LogCapture(sys.stdout, log_callback)

        try:
            result = crew.kickoff()
        finally:
            sys.stdout = original_stdout
            # Stop token polling
            stop_polling.set()
            if poll_thread:
                poll_thread.join(timeout=5)

    # Extract token usage from CrewAI result
    total_tokens = 0
    estimated_cost = Decimal("0")

    if hasattr(result, "token_usage"):
        usage = result.token_usage
        total_input = getattr(usage, "total_tokens", 0) or getattr(usage, "prompt_tokens", 0) or 0
        total_output = getattr(usage, "completion_tokens", 0) or 0
        total_tokens = total_input + total_output
        # Gemini 2.5 Pro pricing: $1.25/1M input, $10/1M output (>200k context)
        # Use lower tier: $1.25/1M input, $10/1M output
        input_cost = Decimal(str(total_input)) * Decimal("0.00000125")
        output_cost = Decimal(str(total_output)) * Decimal("0.00001")
        estimated_cost = (input_cost + output_cost).quantize(Decimal("0.0001"))

    raw_output = str(result.raw) if hasattr(result, "raw") else str(result)

    # Parse the raw output to extract structured data
    parsed = _parse_crew_output(raw_output)

    return {
        "status": parsed["status"],
        "findings": parsed["findings"],
        "tip_of_the_week": parsed["tip_of_the_week"],
        "quote_of_the_week": parsed["quote_of_the_week"],
        "total_tokens": total_tokens,
        "estimated_cost": estimated_cost,
        "raw_output": raw_output,
        "total_dependencies": parsed["total_dependencies"],
        "outdated_count": parsed["outdated_count"],
        "vulnerability_count": parsed["vulnerability_count"],
    }


def _parse_crew_output(raw_output: str) -> dict:
    """
    Parse the crew's raw text output into structured data.
    The LLM output is free-form, so we use heuristics.
    """
    output_lower = raw_output.lower()

    # Determine status
    if any(word in output_lower for word in ["kritiek", "critical", "sunset", "vulnerability found", "cve-"]):
        status = "critical"
    elif any(word in output_lower for word in ["waarschuwing", "warning", "deprecated", "major version"]):
        status = "warning"
    else:
        status = "ok"

    # Count dependencies mentioned
    dep_match = re.search(r"(\d+)\s*(?:packages?|dependencies|pakketten)", output_lower)
    total_deps = int(dep_match.group(1)) if dep_match else 0

    # Extract findings from the output
    findings = []

    # Look for vulnerability mentions
    vuln_count = 0
    vuln_pattern = re.finditer(
        r"\[(CRITICAL|HIGH|MEDIUM)\]\s*((?:CVE|GHSA|PYSEC)-[\w-]+).*?(?:Summary|Beschrijving)?:?\s*(.+?)(?:\n|Fixed|$)",
        raw_output, re.IGNORECASE
    )
    for m in vuln_pattern:
        severity = "critical" if m.group(1).upper() == "CRITICAL" else "warning"
        vuln_count += 1
        findings.append({
            "severity": severity,
            "category": "security",
            "package_name": m.group(2),
            "current_version": "",
            "latest_version": "",
            "summary": m.group(3).strip(),
            "action_steps": "",
        })

    # Look for API deprecation mentions
    if "sunset" in output_lower or "deprecated" in output_lower:
        api_pattern = re.finditer(
            r"(?:API|api).*?(?:sunset|deprecated|end.of.life).*?(?:v[\d.]+|version\s*[\d.]+)",
            raw_output, re.IGNORECASE
        )
        for m in api_pattern:
            findings.append({
                "severity": "critical" if "sunset" in m.group(0).lower() else "warning",
                "category": "api_deprecation",
                "package_name": "API",
                "current_version": "",
                "latest_version": "",
                "summary": m.group(0).strip()[:200],
                "action_steps": "",
            })

    outdated_count = len([f for f in findings if f["category"] in ("outdated", "breaking_change")])

    # Extract tip and quote
    tip = ""
    quote = ""
    tip_match = re.search(r"(?:tip|💡).*?(?:week|dag).*?\n(.+?)(?:\n\n|\n━|$)", raw_output, re.IGNORECASE | re.DOTALL)
    if tip_match:
        tip = tip_match.group(1).strip()[:500]

    quote_match = re.search(r"(?:spreuk|💪|quote).*?(?:week|dag).*?\n(.+?)(?:\n\n|\n━|$)", raw_output, re.IGNORECASE | re.DOTALL)
    if quote_match:
        quote = quote_match.group(1).strip()[:500]

    return {
        "status": status,
        "findings": findings,
        "tip_of_the_week": tip,
        "quote_of_the_week": quote,
        "total_dependencies": total_deps,
        "outdated_count": outdated_count,
        "vulnerability_count": vuln_count,
    }


if __name__ == "__main__":
    results = run_crew()
    print(json.dumps({k: str(v) if isinstance(v, Decimal) else v for k, v in results.items()}, indent=2))
