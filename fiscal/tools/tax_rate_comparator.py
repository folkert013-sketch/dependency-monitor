from pathlib import Path

import yaml
from crewai.tools import BaseTool
from pydantic import Field


class DutchTaxRateComparatorTool(BaseTool):
    name: str = "Dutch Tax Rate Comparator"
    description: str = (
        "Vergelijkt Nederlandse belastingtarieven tussen 2025 en 2026. "
        "Input: een categorie — 'btw', 'ib', 'vpb', 'zelfstandigenaftrek', 'arbeidskorting', 'all' "
        "(of een andere categorie uit de configuratie). "
        "Returns: overzicht van tarieven met wijzigingen (delta)."
    )
    config_path: str = Field(default="")

    def _run(self, category: str = "all") -> str:
        config_file = (
            Path(self.config_path)
            if self.config_path
            else Path(__file__).parent.parent / "config" / "tax_rates.yaml"
        )

        if not config_file.exists():
            return f"ERROR: Tarievenbestand niet gevonden: {config_file}"

        data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
        categories = data.get("tax_rates", {})

        if category.lower() != "all":
            # Filter to matching category
            matched = {k: v for k, v in categories.items() if category.lower() in k.lower()}
            if not matched:
                available = ", ".join(categories.keys())
                return f"Geen tarieven gevonden voor '{category}'. Beschikbare categorieën: {available}"
            categories = matched

        output_parts = []

        for cat_key, cat_data in categories.items():
            label = cat_data.get("label", cat_key)
            items = cat_data.get("items", [])

            lines = [f"## {label}"]

            for item in items:
                name = item.get("name", "")
                val_2025 = item.get("2025", "")
                val_2026 = item.get("2026", "")
                note = item.get("note", "")

                # Calculate delta
                delta = ""
                try:
                    # Handle percentage strings like "21%"
                    v25 = float(str(val_2025).replace("%", "").replace("€", "").replace(".", "").replace(",", ".").strip())
                    v26 = float(str(val_2026).replace("%", "").replace("€", "").replace(".", "").replace(",", ".").strip())
                    diff = v26 - v25
                    if diff > 0:
                        delta = f" (+{diff:g})"
                    elif diff < 0:
                        delta = f" ({diff:g})"
                    else:
                        delta = " (ongewijzigd)"
                except (ValueError, TypeError):
                    if str(val_2025) != str(val_2026):
                        delta = " (gewijzigd)"
                    else:
                        delta = " (ongewijzigd)"

                line = f"| {name} | {val_2025} | {val_2026} |{delta}"
                if note:
                    line += f" — {note}"
                lines.append(line)

            output_parts.append("\n".join(lines))

        header = "Vergelijking belastingtarieven 2025 vs 2026:\n\n| Onderdeel | 2025 | 2026 | Wijziging |\n|-----------|------|------|-----------|\n"

        return header + "\n\n".join(output_parts)
