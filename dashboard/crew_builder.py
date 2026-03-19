"""
Dynamic crew builder — creates a CrewAI Crew from a Team database record.
"""

import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from .tool_registry import TOOL_REGISTRY

PROVIDER_CONFIG = {
    "gemini": {"prefix": "gemini/", "env_key": "GEMINI_API_KEY"},
    "anthropic": {"prefix": "anthropic/", "env_key": "ANTHROPIC_API_KEY"},
    "openai": {"prefix": "openai/", "env_key": "OPENAI_API_KEY"},
}

SUGGESTED_MODELS = {
    "gemini": ["gemini-3-flash-preview", "gemini-3.1-pro-preview"],
    "anthropic": ["claude-sonnet-4-6", "claude-haiku-4-5"],
    "openai": ["gpt-4o", "gpt-4o-mini"],
}


def _get_llm(provider: str, model_id: str) -> LLM:
    config = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["gemini"])
    return LLM(
        model=f"{config['prefix']}{model_id}",
        api_key=os.environ.get(config["env_key"], ""),
    )


def _interpolate(text: str, variables: dict) -> str:
    """Replace {var_name} placeholders with actual values."""
    for key, value in variables.items():
        text = text.replace(f"{{{key}}}", str(value))
    return text


def _validate_path(user_path: str) -> str | None:
    """Validate that a user-supplied path stays within MONITORED_PROJECT_PATH (H2)."""
    from django.conf import settings as django_settings

    base = Path(django_settings.MONITORED_PROJECT_PATH).resolve()
    try:
        resolved = Path(user_path).resolve()
    except (OSError, ValueError):
        return None
    if not str(resolved).startswith(str(base)):
        return None
    return str(resolved)


def _instantiate_tool(tool_id: str, run_variables: dict):
    """Create a single tool instance, passing relevant kwargs."""
    entry = TOOL_REGISTRY.get(tool_id)
    if not entry:
        return None
    cls = entry["cls"]

    # Special handling for tools that need constructor arguments
    if tool_id == "requirements_reader":
        req_path = run_variables.get("requirements_path", "")
        if req_path:
            safe_path = _validate_path(req_path)
            if not safe_path:
                return None
            return cls(requirements_path=safe_path)
    elif tool_id == "api_status_checker":
        config_path = str(Path(__file__).parent.parent / "monitor" / "config" / "monitored_apis.yaml")
        return cls(config_path=config_path)
    elif tool_id == "deadline_checker":
        config_path = str(Path(__file__).parent.parent / "fiscal" / "config" / "fiscal_sources.yaml")
        return cls(config_path=config_path)
    elif tool_id == "tax_rate_comparator":
        config_path = str(Path(__file__).parent.parent / "fiscal" / "config" / "tax_rates.yaml")
        return cls(config_path=config_path)

    # Default: no-arg instantiation
    try:
        return cls()
    except TypeError:
        return None


def build_crew_from_team(team, run_variables: dict, step_callback=None, task_callback=None):
    """
    Build a CrewAI Crew from a Team database record.

    Args:
        team: Team model instance (with prefetched agents/tasks)
        run_variables: dict of variable values for interpolation
        step_callback: optional CrewAI step callback
        task_callback: optional CrewAI task callback

    Returns:
        (crew, agents_list)
    """
    db_agents = list(team.agents.all().order_by("order"))
    db_tasks = list(team.tasks.all().order_by("order"))

    # --- Build agents ---
    agent_map = {}  # db_agent.pk -> CrewAI Agent
    agents_list = []

    for db_agent in db_agents:
        llm = _get_llm(db_agent.llm_provider, db_agent.llm_model)

        tool_instances = []
        for tool_id in (db_agent.tools or []):
            tool = _instantiate_tool(tool_id, run_variables)
            if tool:
                tool_instances.append(tool)

        agent = Agent(
            role=db_agent.role,
            goal=_interpolate(db_agent.goal, run_variables),
            backstory=_interpolate(db_agent.backstory, run_variables),
            tools=tool_instances,
            llm=llm,
            max_iter=db_agent.max_iter,
            verbose=db_agent.verbose,
        )
        agent_map[db_agent.pk] = agent
        agents_list.append(agent)

    # --- Build tasks (first pass — no context yet) ---
    task_map = {}  # db_task.pk -> CrewAI Task
    tasks_list = []

    for db_task in db_tasks:
        crewai_agent = agent_map.get(db_task.agent_id)
        if not crewai_agent:
            continue

        task = Task(
            description=_interpolate(db_task.description, run_variables),
            expected_output=_interpolate(db_task.expected_output, run_variables),
            agent=crewai_agent,
        )
        task_map[db_task.pk] = task
        tasks_list.append(task)

    # --- Second pass: wire context tasks ---
    for db_task in db_tasks:
        crewai_task = task_map.get(db_task.pk)
        if not crewai_task:
            continue
        ctx_pks = list(db_task.context_tasks.values_list("pk", flat=True))
        if ctx_pks:
            crewai_task.context = [task_map[pk] for pk in ctx_pks if pk in task_map]

    # --- Build crew ---
    process = Process.sequential if team.process == "sequential" else Process.hierarchical

    crew_kwargs = dict(
        agents=agents_list,
        tasks=tasks_list,
        process=process,
        verbose=team.verbose,
    )
    if step_callback:
        crew_kwargs["step_callback"] = step_callback
    if task_callback:
        crew_kwargs["task_callback"] = task_callback

    crew = Crew(**crew_kwargs)
    return crew, agents_list
