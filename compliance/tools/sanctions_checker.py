import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


class SanctionsCheckerTool(BaseTool):
    name: str = "Sanctions Checker"
    description: str = (
        "Doorzoekt publieke sanctielijsten op personen of entiteiten. "
        "Input: een naam van een persoon of organisatie. "
        "Returns: gevonden vermeldingen op EU, NL en VN sanctielijsten."
    )

    SOURCES: list = [
        {
            "name": "EU Consolidated Sanctions",
            "search_url": "https://www.sanctionsmap.eu/#/main?search={query}",
            "fallback_url": "https://data.europa.eu/euodp/en/data/dataset/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions",
        },
        {
            "name": "NL Nationaal Sanctieoverzicht",
            "search_url": "https://www.rijksoverheid.nl/onderwerpen/internationale-sancties/inhoud/sanctielijsten",
            "fallback_url": "https://www.rijksoverheid.nl/onderwerpen/internationale-sancties",
        },
        {
            "name": "VN Sanctielijst (Security Council)",
            "search_url": "https://www.un.org/securitycouncil/content/un-sc-consolidated-list",
            "fallback_url": "https://www.un.org/securitycouncil/sanctions/information",
        },
    ]

    def _run(self, entity_name: str) -> str:
        results = []

        for source in self.SOURCES:
            try:
                url = source.get("search_url", source["fallback_url"]).format(
                    query=requests.utils.quote(entity_name)
                )
                resp = requests.get(url, timeout=15, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FenoFinMonitor/1.0)"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Search page text for mentions of the entity
                page_text = soup.get_text(separator=" ", strip=True).lower()
                name_lower = entity_name.lower()

                if name_lower in page_text:
                    # Extract surrounding context
                    idx = page_text.find(name_lower)
                    start = max(0, idx - 100)
                    end = min(len(page_text), idx + len(name_lower) + 200)
                    context = page_text[start:end].strip()
                    results.append(
                        f"Bron: {source['name']}\n"
                        f"  GEVONDEN: '{entity_name}' komt voor op deze sanctielijst.\n"
                        f"  Context: ...{context}...\n"
                        f"  URL: {url}"
                    )
                else:
                    results.append(
                        f"Bron: {source['name']}\n"
                        f"  Geen vermelding gevonden voor '{entity_name}'.\n"
                        f"  URL: {url}"
                    )

            except requests.RequestException as e:
                results.append(f"Bron: {source['name']}\n  ERROR: {e}")

        return "\n\n".join(results)
