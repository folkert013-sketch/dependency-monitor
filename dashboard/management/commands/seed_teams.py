"""
Management command: seed AI teams from JSON fixture files.

Usage:
    python manage.py seed_teams              # seed all teams
    python manage.py seed_teams --team wwft-compliance  # seed one team
    python manage.py seed_teams --force      # overwrite existing teams
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from dashboard.models import Team, TeamAgent, TeamTask, TeamVariable

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "teams"


class Command(BaseCommand):
    help = "Seed AI teams from JSON fixture files in dashboard/fixtures/teams/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--team",
            type=str,
            default=None,
            help="Slug of a specific team to seed (e.g. wwft-compliance)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Overwrite existing teams (delete + recreate)",
        )

    def handle(self, *args, **options):
        team_slug = options["team"]
        force = options["force"]

        if team_slug:
            fixture_path = FIXTURES_DIR / f"{team_slug}.json"
            if not fixture_path.exists():
                self.stderr.write(self.style.ERROR(f"Fixture not found: {fixture_path}"))
                return
            fixtures = [fixture_path]
        else:
            fixtures = sorted(FIXTURES_DIR.glob("*.json"))

        if not fixtures:
            self.stderr.write(self.style.WARNING("No fixture files found."))
            return

        for fixture_path in fixtures:
            self._seed_team(fixture_path, force=force)

    def _seed_team(self, fixture_path: Path, force: bool = False):
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        slug = data["slug"]
        existing = Team.objects.filter(slug=slug).first()

        if existing and not force:
            self.stdout.write(self.style.WARNING(f"  Skipped '{slug}' (already exists, use --force to overwrite)"))
            return

        if existing and force:
            existing.delete()
            self.stdout.write(f"  Deleted existing team '{slug}'")

        # Create team
        team = Team.objects.create(
            name=data["name"],
            slug=slug,
            description=data.get("description", ""),
            process=data.get("process", "sequential"),
            verbose=data.get("verbose", True),
        )

        # Create variables
        for var_data in data.get("variables", []):
            TeamVariable.objects.create(
                team=team,
                name=var_data["name"],
                label=var_data["label"],
                description=var_data.get("description", ""),
                input_type=var_data.get("input_type", "text"),
                default_value=var_data.get("default_value", ""),
                required=var_data.get("required", True),
                order=var_data.get("order", 0),
            )

        # Create agents (indexed by order for task linking)
        agent_by_order = {}
        for agent_data in data.get("agents", []):
            agent = TeamAgent.objects.create(
                team=team,
                order=agent_data["order"],
                role=agent_data["role"],
                goal=agent_data["goal"],
                backstory=agent_data.get("backstory", ""),
                llm_provider=agent_data.get("llm_provider", "gemini"),
                llm_model=agent_data.get("llm_model", "gemini-3-flash-preview"),
                tools=agent_data.get("tools", []),
                max_iter=agent_data.get("max_iter", 25),
                verbose=agent_data.get("verbose", True),
            )
            agent_by_order[agent_data["order"]] = agent

        # Create tasks (two passes: create, then wire context)
        task_by_order = {}
        for task_data in data.get("tasks", []):
            agent = agent_by_order.get(task_data["agent_order"])
            if not agent:
                continue
            task = TeamTask.objects.create(
                team=team,
                order=task_data["order"],
                description=task_data["description"],
                expected_output=task_data.get("expected_output", ""),
                agent=agent,
            )
            task_by_order[task_data["order"]] = task

        # Wire context_tasks M2M
        for task_data in data.get("tasks", []):
            task = task_by_order.get(task_data["order"])
            if not task:
                continue
            ctx_orders = task_data.get("context_task_orders", [])
            if ctx_orders:
                ctx_tasks = [task_by_order[o] for o in ctx_orders if o in task_by_order]
                task.context_tasks.set(ctx_tasks)

        self.stdout.write(self.style.SUCCESS(f"  Seeded team '{slug}' ({len(agent_by_order)} agents, {len(task_by_order)} tasks)"))
