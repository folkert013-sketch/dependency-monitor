"""
Dynamic crew builder — creates a CrewAI Crew from a Team database record.
"""

import logging
import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from .constants import PROVIDER_CONFIG, SUGGESTED_MODELS
from .tool_registry import TOOL_REGISTRY

logger = logging.getLogger(__name__)


def get_model_ids(provider):
    """Return flat list of model IDs for a provider (backward compat)."""
    return [m["id"] for m in SUGGESTED_MODELS.get(provider, [])]


def _get_llm(provider: str, model_id: str) -> LLM:
    config = PROVIDER_CONFIG.get(provider, PROVIDER_CONFIG["gemini"])
    api_key = os.environ.get(config["env_key"], "")
    if not api_key:
        raise ValueError(
            f"API key ontbreekt: stel {config['env_key']} in als environment variabele"
        )
    return LLM(
        model=f"{config['prefix']}{model_id}",
        api_key=api_key,
    )


_PROMPT_INJECTION_PATTERNS = [
    "ignore all previous",
    "ignore your instructions",
    "disregard your",
    "forget your instructions",
    "new instructions:",
    "system prompt:",
    "you are now",
    "act as if",
]


def _sanitize_variable(value: str) -> str:
    """Strip known prompt injection patterns from user-supplied variable values."""
    lower = value.lower()
    for pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern in lower:
            logger.warning("Prompt injection attempt detected in variable value: %s...", value[:50])
            return "[GEBLOKKEERD — ongeldige invoer]"
    # Limit variable length to prevent context stuffing
    if len(value) > 5000:
        return value[:5000]
    return value


def _interpolate(text: str, variables: dict) -> str:
    """Replace {var_name} placeholders with sanitized values."""
    for key, value in variables.items():
        sanitized = _sanitize_variable(str(value))
        text = text.replace(f"{{{key}}}", sanitized)
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
    except TypeError as e:
        logger.warning("Tool '%s' kon niet worden geïnstantieerd: %s", tool_id, e)
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

    # --- Build select-opties tools mapping ---
    # Voor select-variabelen met tools in de opties: bouw een mapping
    # zodat agent tools met {var_naam} automatisch vervangen worden.
    select_tools_map = {}  # {var_name: [tool_ids]}
    for db_var in team.variables.filter(input_type="select"):
        selected_value = run_variables.get(db_var.name, db_var.default_value)
        for option in (db_var.options or []):
            if option.get("value") == selected_value and "tools" in option:
                select_tools_map[db_var.name] = option["tools"]

    # --- Build agents ---
    agent_map = {}  # db_agent.pk -> CrewAI Agent
    agents_list = []

    for db_agent in db_agents:
        llm = _get_llm(db_agent.llm_provider, db_agent.llm_model)

        tool_instances = []
        expanded_vars = set()  # Track welke select-vars al expanded zijn
        for raw_tool_id in (db_agent.tools or []):
            # Check of dit tool-ID een select-variabele met tools bevat
            matched_var = None
            for var_name, mapped_tools in select_tools_map.items():
                if f"{{{var_name}}}" in raw_tool_id:
                    matched_var = var_name
                    break

            if matched_var and matched_var not in expanded_vars:
                # Eerste keer dat we deze var tegenkomen: laad alle mapped tools
                expanded_vars.add(matched_var)
                for mapped_id in select_tools_map[matched_var]:
                    tool = _instantiate_tool(mapped_id, run_variables)
                    if tool:
                        tool_instances.append(tool)
            elif matched_var:
                # Deze var is al expanded, skip (voorkom duplicaten)
                continue
            else:
                # Geen select-mapping: gewone interpolatie
                tool_id = _interpolate(raw_tool_id, run_variables)
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

    # For hierarchical process, pass the designated manager agent
    # and exclude it from the workers list
    if team.process == "hierarchical":
        manager_db = next((a for a in db_agents if a.is_manager), None)
        if manager_db:
            manager_agent = agent_map.get(manager_db.pk)
            if manager_agent:
                # CrewAI requires the manager agent to have no tools
                manager_agent.tools = []
                crew_kwargs["manager_agent"] = manager_agent
                agents_list = [a for a in agents_list if a is not manager_agent]
                crew_kwargs["agents"] = agents_list

    if step_callback:
        crew_kwargs["step_callback"] = step_callback
    if task_callback:
        crew_kwargs["task_callback"] = task_callback

    crew = Crew(**crew_kwargs)
    return crew, agents_list
