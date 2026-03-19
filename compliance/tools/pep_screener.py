import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


class PEPScreenerTool(BaseTool):
    name: str = "PEP Screener"
    description: str = (
        "Doorzoekt publieke bronnen op Politically Exposed Persons (PEP). "
        "Input: een naam van een persoon. "
        "Returns: gevonden vermeldingen bij Tweede Kamer, Eerste Kamer, Rijksoverheid en Europees Parlement."
    )

    SOURCES: list = [
        {
            "name": "Tweede Kamer",
            "url": "https://www.tweedekamer.nl",
            "search_url": "https://www.tweedekamer.nl/zoeken?qry={query}",
        },
        {
            "name": "Eerste Kamer",
            "url": "https://www.eerstekamer.nl",
            "search_url": "https://www.eerstekamer.nl/zoeken?zoekterm={query}",
        },
        {
            "name": "Rijksoverheid",
            "url": "https://www.rijksoverheid.nl",
            "search_url": "https://www.rijksoverheid.nl/zoeken?trefwoord={query}",
        },
        {
            "name": "Europees Parlement",
            "url": "https://www.europarl.europa.eu",
            "search_url": "https://www.europarl.europa.eu/meps/nl/search/table?name={query}",
        },
    ]

    def _run(self, person_name: str) -> str:
        results = []

        for source in self.SOURCES:
            search_url = source["search_url"].format(
                query=requests.utils.quote(person_name)
            )
            try:
                resp = requests.get(search_url, timeout=15, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FenoFinMonitor/1.0)"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Look for relevant links/mentions
                mentions = []
                page_text = soup.get_text(separator=" ", strip=True)
                name_parts = person_name.lower().split()

                for link in soup.find_all("a", href=True):
                    title = link.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    title_lower = title.lower()
                    # Check if any significant name part appears in the link text
                    if any(part in title_lower for part in name_parts if len(part) > 2):
                        href = link["href"]
                        if not href.startswith("http"):
                            href = f"{source['url'].rstrip('/')}/{href.lstrip('/')}"
                        mentions.append(f"  - {title}\n    URL: {href}")
                    if len(mentions) >= 5:
                        break

                if mentions:
                    results.append(
                        f"Bron: {source['name']}\n"
                        f"  MOGELIJKE PEP-VERMELDING(EN):\n" + "\n".join(mentions)
                    )
                else:
                    results.append(
                        f"Bron: {source['name']}\n"
                        f"  Geen PEP-vermelding gevonden voor '{person_name}'.\n"
                        f"  URL: {search_url}"
                    )

            except requests.RequestException as e:
                results.append(f"Bron: {source['name']}\n  ERROR: {e}")

        return "\n\n".join(results)
