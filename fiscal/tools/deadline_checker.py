from datetime import date, timedelta
from pathlib import Path

import yaml
from crewai.tools import BaseTool
from pydantic import Field


class FiscalDeadlineCheckerTool(BaseTool):
    name: str = "Fiscal Deadline Checker"
    description: str = (
        "Checkt aankomende fiscale deadlines voor het MKB vanuit de configuratie. "
        "Input: 'all' voor alle deadlines, of een categorie (bijv. 'btw', 'ib', 'vpb', 'loonbelasting'). "
        "Returns: lijst van aankomende deadlines met datum, beschrijving en urgentie."
    )
    config_path: str = Field(default="")

    def _run(self, category: str = "all") -> str:
        config_file = (
            Path(self.config_path)
            if self.config_path
            else Path(__file__).parent.parent / "config" / "fiscal_sources.yaml"
        )

        if not config_file.exists():
            return f"ERROR: Config bestand niet gevonden: {config_file}"

        config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
        deadlines = config.get("deadlines", [])

        if category.lower() != "all":
            deadlines = [d for d in deadlines if category.lower() in d.get("category", "").lower()]

        today = date.today()
        upcoming = []

        for dl in deadlines:
            try:
                dl_date = date.fromisoformat(dl["date"])
            except (ValueError, KeyError):
                continue

            days_until = (dl_date - today).days
            if days_until < -30:  # Skip deadlines more than 30 days in the past
                continue

            if days_until < 0:
                urgency = "VERLOPEN"
            elif days_until <= 7:
                urgency = "URGENT"
            elif days_until <= 30:
                urgency = "BINNENKORT"
            elif days_until <= 90:
                urgency = "KOMEND"
            else:
                urgency = "LATER"

            upcoming.append(
                f"[{urgency}] {dl['date']} — {dl.get('description', 'Geen beschrijving')}\n"
                f"  Categorie: {dl.get('category', 'algemeen')}\n"
                f"  Dagen tot deadline: {days_until}"
            )

        if not upcoming:
            return f"Geen aankomende deadlines gevonden voor categorie '{category}'."

        return f"Fiscale deadlines (vandaag: {today}):\n\n" + "\n\n".join(upcoming)
