import os
from pathlib import Path

import yaml
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from .tools import (
    APIStatusCheckerTool,
    EmailSenderTool,
    GitHubChangelogTool,
    PyPIVersionCheckerTool,
    RequirementsReaderTool,
    VulnerabilityScannerTool,
)

CONFIG_DIR = Path(__file__).parent / "config"

# Ordered list of agent roles matching the sequential task execution order
AGENT_SEQUENCE = [
    "Dependency Scanner",
    "API Deprecation Monitor",
    "Security Vulnerability Checker",
    "Breaking Change Analyzer",
    "Action Report Writer",
]


def _load_yaml(filename: str) -> dict:
    return yaml.safe_load((CONFIG_DIR / filename).read_text(encoding="utf-8"))


def create_crew(requirements_path: str, step_callback=None, task_callback=None) -> tuple[Crew, list[Agent]]:
    """Create and return the dependency monitor crew and its agents."""
    agents_config = _load_yaml("agents.yaml")
    tasks_config = _load_yaml("tasks.yaml")

    # Hoofd-agent: pro model voor rapportage en synthese
    manager_model = os.environ.get("CREW_MANAGER_MODEL", "gemini-3.1-pro-preview")
    manager_llm = LLM(
        model=f"gemini/{manager_model}",
        api_key=os.environ.get("GEMINI_API_KEY", ""),
    )

    # Taak-agents: flash model voor snelle uitvoering
    task_model = os.environ.get("CREW_TASK_MODEL", "gemini-3.1-flash-lite-preview")
    task_llm = LLM(
        model=f"gemini/{task_model}",
        api_key=os.environ.get("GEMINI_API_KEY", ""),
    )

    # --- Tools ---
    requirements_tool = RequirementsReaderTool(requirements_path=requirements_path)
    pypi_tool = PyPIVersionCheckerTool()
    api_status_tool = APIStatusCheckerTool(
        config_path=str(CONFIG_DIR / "monitored_apis.yaml")
    )
    vuln_tool = VulnerabilityScannerTool()
    changelog_tool = GitHubChangelogTool()
    email_tool = EmailSenderTool()

    # --- Agents (flash voor taken, pro voor rapportage) ---
    dependency_scanner = Agent(
        **agents_config["dependency_scanner"],
        tools=[requirements_tool, pypi_tool],
        llm=task_llm,
        max_iter=80,  # Needs ~2 calls per package (read + check) for ~35 packages
    )

    api_monitor = Agent(
        **agents_config["api_deprecation_monitor"],
        tools=[api_status_tool],
        llm=task_llm,
        max_iter=40,  # ~14 APIs to check
    )

    security_checker = Agent(
        **agents_config["security_checker"],
        tools=[vuln_tool],
        llm=task_llm,
        max_iter=50,  # 1 call per package with vulnerabilities
    )

    breaking_analyzer = Agent(
        **agents_config["breaking_change_analyzer"],
        tools=[changelog_tool],
        llm=task_llm,
        max_iter=40,  # Only checks outdated packages
    )

    report_writer = Agent(
        **agents_config["action_report_writer"],
        tools=[email_tool],
        llm=manager_llm,
    )

    # --- Tasks ---
    scan_task = Task(
        **{k: v for k, v in tasks_config["scan_dependencies"].items() if k != "agent"},
        agent=dependency_scanner,
    )
    # Interpolate requirements_path
    scan_task.description = scan_task.description.replace(
        "{requirements_path}", requirements_path
    )

    api_task = Task(
        **{k: v for k, v in tasks_config["check_api_status"].items() if k != "agent"},
        agent=api_monitor,
    )

    vuln_task = Task(
        **{k: v for k, v in tasks_config["check_vulnerabilities"].items() if k != "agent"},
        agent=security_checker,
        context=[scan_task],
    )

    breaking_task = Task(
        **{k: v for k, v in tasks_config["analyze_breaking_changes"].items() if k != "agent"},
        agent=breaking_analyzer,
        context=[scan_task],
    )

    report_task = Task(
        **{k: v for k, v in tasks_config["compile_and_send_report"].items() if k != "agent"},
        agent=report_writer,
        context=[scan_task, api_task, vuln_task, breaking_task],
    )

    # --- Crew ---
    crew_kwargs = dict(
        agents=[dependency_scanner, api_monitor, security_checker, breaking_analyzer, report_writer],
        tasks=[scan_task, api_task, vuln_task, breaking_task, report_task],
        process=Process.sequential,
        verbose=True,
    )
    if step_callback:
        crew_kwargs["step_callback"] = step_callback
    if task_callback:
        crew_kwargs["task_callback"] = task_callback

    crew = Crew(**crew_kwargs)
    agents = [dependency_scanner, api_monitor, security_checker, breaking_analyzer, report_writer]

    return crew, agents
