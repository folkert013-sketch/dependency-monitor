"""
Entry point for running the dependency monitor crew.
Can be called from Django management command or standalone.
"""

import json
import os
import re
import sys
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")


def run_crew(requirements_path: str | None = None) -> dict:
    """
    Run the CrewAI crew and return structured results.

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
    from .crew import create_crew

    if not requirements_path:
        requirements_path = os.environ.get(
            "MONITORED_PROJECT_PATH",
            str(Path(__file__).parent.parent.parent / "django-finance-project_2"),
        )
        requirements_path = str(Path(requirements_path) / "requirements.txt")

    print(f"[Monitor] Scanning: {requirements_path}")
    crew = create_crew(requirements_path)

    result = crew.kickoff()

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
