"""
VPB Tarievenlijst Tool — zoekt VPB-tarieven en drempels op per boekjaar.
"""

import re
from pathlib import Path

from crewai.tools import BaseTool

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

_MAX_RESULT_LEN = 8000


def _search_tarievenlijst(filepath: Path, query: str) -> str:
    """Zoek secties in een tarievenlijst md-bestand op basis van trefwoord."""
    text = filepath.read_text(encoding="utf-8")

    # Splits op H2 kopjes
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    query_lower = query.lower()
    matches = []
    for section in sections:
        if not section.strip():
            continue
        # Zoek in de sectietitel en -inhoud
        if query_lower in section.lower():
            matches.append(section.strip())

    if matches:
        result = "\n\n---\n\n".join(matches)
    else:
        # Geen match: retourneer het hele document (compact genoeg)
        result = text

    if len(result) > _MAX_RESULT_LEN:
        result = result[:_MAX_RESULT_LEN] + "\n\n[... afgekapt]"
    return result


class VpbTarievenTool(BaseTool):
    name: str = "vpb_tarieven"
    description: str = (
        "Zoekt VPB-tarieven, drempels en bedragen op voor een specifiek boekjaar. "
        "Input formaat: 'trefwoord | boekjaar', bijv. 'tarief | 2023', "
        "'kia | 2023', 'verliesverrekening | 2023'. "
        "Het boekjaar is verplicht."
    )

    def _run(self, query: str = "") -> str:
        if not query or not query.strip():
            return "Geef een trefwoord en boekjaar, bijv. 'tarief | 2023'"

        # Parse query: 'trefwoord | boekjaar' of 'trefwoord boekjaar'
        if "|" in query:
            parts = query.split("|", 1)
            search_term = parts[0].strip()
            boekjaar = parts[1].strip()
        else:
            # Probeer een 4-cijferig jaartal te vinden
            year_match = re.search(r"\b(20\d{2})\b", query)
            if year_match:
                boekjaar = year_match.group(1)
                search_term = query.replace(boekjaar, "").strip()
            else:
                return (
                    "Boekjaar ontbreekt. Geef input als 'trefwoord | boekjaar', "
                    "bijv. 'tarief | 2023'."
                )

        filepath = _CONFIG_DIR / f"vpb_tarieven_{boekjaar}.md"
        if not filepath.is_file():
            return (
                f"Geen VPB-tarievenlijst beschikbaar voor boekjaar {boekjaar}. "
                f"Beschikbare bestanden: {', '.join(p.stem for p in _CONFIG_DIR.glob('vpb_tarieven_*.md'))}"
            )

        if not search_term:
            # Geen trefwoord: retourneer alles
            text = filepath.read_text(encoding="utf-8")
            if len(text) > _MAX_RESULT_LEN:
                text = text[:_MAX_RESULT_LEN] + "\n\n[... afgekapt]"
            return text

        return _search_tarievenlijst(filepath, search_term)
