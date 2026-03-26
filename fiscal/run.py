"""
Entry point for running the fiscal monitor crew.
Can be called from Django views or standalone.
"""

import io
import json
import logging
import re
import sys
import threading
from decimal import Decimal
from pathlib import Path

logger = logging.getLogger(__name__)

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

_stdout_lock = threading.Lock()


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
            if not line:
                continue
            if "Agent:" in line or "agent:" in line:
                self._callback("agent", "", line)
            elif "Tool:" in line or "tool:" in line or "Using tool:" in line:
                self._callback("tool", "", line)
            elif "Thought:" in line or "thinking" in line.lower():
                self._callback("thought", "", line[:300])
            elif any(kw in line.lower() for kw in ["final answer", "finished", "result"]):
                self._callback("result", "", line[:400])
            elif len(line) > 10:
                self._callback("info", "", line[:400])

    def flush(self):
        self._original.flush()


def run_fiscal_crew(log_callback=None) -> dict:
    """
    Run the fiscal CrewAI crew and return structured results.

    Returns a dict with:
        - articles: list of article dicts (title, intro, body, category, sources, quality_score)
        - total_tokens: int
        - estimated_cost: Decimal
        - raw_output: str
    """
    from .crew import create_crew

    # Build CrewAI callbacks that feed our log_callback
    step_cb = None
    task_cb = None
    if log_callback:
        def step_cb(step_output):
            try:
                agent = getattr(step_output, "agent", None)
                agent_name = getattr(agent, "role", "") if agent else ""
                output_text = getattr(step_output, "output", "")
                thought = getattr(step_output, "thought", "")
                tool = getattr(step_output, "tool", "")

                if tool:
                    log_callback("tool", agent_name, f"Tool: {tool}")
                if thought:
                    short = thought[:300] + ("..." if len(thought) > 300 else "")
                    log_callback("thought", agent_name, short)
                if output_text and not tool:
                    short = str(output_text)[:400] + ("..." if len(str(output_text)) > 400 else "")
                    log_callback("result", agent_name, short)
            except Exception:
                logger.debug("Error in step_cb", exc_info=True)

        def task_cb(task_output):
            try:
                desc = getattr(task_output, "description", "")
                agent = getattr(task_output, "agent", "")
                summary = str(getattr(task_output, "raw", ""))[:300]
                log_callback("task_done", str(agent), f"Taak afgerond: {desc[:100]}\n{summary}")
            except Exception:
                logger.debug("Error in task_cb", exc_info=True)

    crew = create_crew(step_callback=step_cb, task_callback=task_cb)

    if log_callback:
        log_callback("start", "Crew", "Fiscale crew gestart — agents worden uitgevoerd...")

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

    # Extract token usage
    total_tokens = 0
    total_input = 0
    total_output = 0
    estimated_cost = Decimal("0")

    if hasattr(result, "token_usage"):
        usage = result.token_usage
        total_input = getattr(usage, "prompt_tokens", 0) or 0
        total_output = getattr(usage, "completion_tokens", 0) or 0
        total_tokens = getattr(usage, "total_tokens", 0) or (total_input + total_output)
        input_cost = Decimal(str(total_input)) * Decimal("0.00000125")
        output_cost = Decimal(str(total_output)) * Decimal("0.00001")
        estimated_cost = (input_cost + output_cost).quantize(Decimal("0.0001"))

    raw_output = str(result.raw) if hasattr(result, "raw") else str(result)

    # Parse articles from the output
    articles = _parse_fiscal_output(raw_output)

    return {
        "articles": articles,
        "total_tokens": total_tokens,
        "total_input": total_input,
        "total_output": total_output,
        "estimated_cost": estimated_cost,
        "raw_output": raw_output,
    }


def _validate_article(art: dict) -> dict | None:
    """Validate and normalize a single article dict. Returns None if invalid."""
    if "title" not in art or "body" not in art:
        return None
    try:
        quality = min(10, max(1, int(art.get("quality_score", 5))))
    except (ValueError, TypeError):
        quality = 5
    return {
        "title": str(art.get("title", ""))[:300],
        "intro": str(art.get("intro", ""))[:1000],
        "body": str(art.get("body", "")),
        "category": str(art.get("category", "algemeen")).lower(),
        "sources": art.get("sources", []) if isinstance(art.get("sources"), list) else [],
        "quality_score": quality,
        "key_takeaways": art.get("key_takeaways", []) if isinstance(art.get("key_takeaways"), list) else [],
        "action_items": art.get("action_items", []) if isinstance(art.get("action_items"), list) else [],
        "deadline_date": str(art["deadline_date"])[:10] if art.get("deadline_date") else None,
        "relevance_tags": art.get("relevance_tags", []) if isinstance(art.get("relevance_tags"), list) else [],
    }


def _extract_json_objects(text: str) -> list[str]:
    """Extract top-level JSON object strings from text using balanced-brace matching."""
    results = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            depth = 0
            start = i
            in_string = False
            escape_next = False
            for j in range(i, len(text)):
                ch = text[j]
                if escape_next:
                    escape_next = False
                    continue
                if ch == "\\":
                    escape_next = True
                    continue
                if ch == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        results.append(text[start:j + 1])
                        i = j + 1
                        break
            else:
                i += 1
        else:
            i += 1
    return results


def _parse_fiscal_output(raw_output: str) -> list:
    """
    Parse the crew's raw output to extract article JSON array.
    The quality reviewer should output a JSON array, but we handle edge cases.
    """
    # Try to find a JSON array in the output
    # Look for [...] pattern
    json_match = re.search(r'\[\s*\{.*?\}\s*\]', raw_output, re.DOTALL)
    if json_match:
        try:
            articles = json.loads(json_match.group())
            if isinstance(articles, list) and all(isinstance(a, dict) for a in articles):
                valid = [v for a in articles if (v := _validate_article(a)) is not None]
                if valid:
                    return valid
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: extract individual JSON objects using balanced-brace matching
    articles = []
    for obj_str in _extract_json_objects(raw_output):
        if '"title"' not in obj_str:
            continue
        try:
            art = json.loads(obj_str)
            validated = _validate_article(art)
            if validated:
                articles.append(validated)
        except (json.JSONDecodeError, ValueError):
            continue

    return articles


if __name__ == "__main__":
    results = run_fiscal_crew()
    print(json.dumps(
        {k: str(v) if isinstance(v, Decimal) else v for k, v in results.items()},
        indent=2, ensure_ascii=False,
    ))
