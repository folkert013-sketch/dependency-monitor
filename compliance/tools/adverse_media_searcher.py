import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


class AdverseMediaSearcherTool(BaseTool):
    name: str = "Adverse Media Searcher"
    description: str = (
        "Doorzoekt Nederlandse nieuwsbronnen op negatieve berichtgeving over een persoon of organisatie. "
        "Input: een naam van een persoon of organisatie. "
        "Returns: gevonden nieuwsberichten van NU.nl, NOS, Rechtspraak.nl en FD."
    )

    SOURCES: list = [
        {
            "name": "NU.nl",
            "url": "https://www.nu.nl",
            "search_url": "https://www.nu.nl/zoeken/?q={query}",
        },
        {
            "name": "NOS",
            "url": "https://nos.nl",
            "search_url": "https://nos.nl/zoeken/?q={query}",
        },
        {
            "name": "Rechtspraak.nl",
            "url": "https://www.rechtspraak.nl",
            "search_url": "https://www.rechtspraak.nl/Uitspraken/paginas/default.aspx?SearchTerms={query}",
        },
        {
            "name": "Het Financieele Dagblad",
            "url": "https://fd.nl",
            "search_url": "https://fd.nl/zoeken?q={query}",
        },
    ]

    NEGATIVE_KEYWORDS: list = [
        "fraude", "witwassen", "oplichting", "verdacht", "aangehouden",
        "veroordeeld", "strafbaar", "sanctie", "boete", "illegaal",
        "corruptie", "omkoping", "belastingontduiking", "faillissement",
        "bestuursverbod", "overtreding", "misdrijf",
    ]

    def _run(self, entity_name: str) -> str:
        results = []

        for source in self.SOURCES:
            search_url = source["search_url"].format(
                query=requests.utils.quote(entity_name)
            )
            try:
                resp = requests.get(search_url, timeout=15, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FenoFinMonitor/1.0)"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                articles = []
                for link in soup.find_all("a", href=True):
                    title = link.get_text(strip=True)
                    href = link["href"]
                    if len(title) < 15 or len(title) > 200 or href.startswith("#"):
                        continue
                    if not href.startswith("http"):
                        base = source["url"].rstrip("/")
                        href = f"{base}/{href.lstrip('/')}"

                    # Check for adverse/negative keywords
                    title_lower = title.lower()
                    name_lower = entity_name.lower()
                    name_parts = name_lower.split()

                    has_name = any(part in title_lower for part in name_parts if len(part) > 2)
                    has_negative = any(kw in title_lower for kw in self.NEGATIVE_KEYWORDS)

                    if has_name or has_negative:
                        flag = " [NEGATIEF]" if has_negative else ""
                        articles.append(f"  - {title}{flag}\n    URL: {href}")

                    if len(articles) >= 5:
                        break

                if articles:
                    results.append(
                        f"Bron: {source['name']}\n"
                        f"  Gevonden berichten:\n" + "\n".join(articles)
                    )
                else:
                    results.append(
                        f"Bron: {source['name']}\n"
                        f"  Geen relevante berichten gevonden voor '{entity_name}'.\n"
                        f"  URL: {search_url}"
                    )

            except requests.RequestException as e:
                results.append(f"Bron: {source['name']}\n  ERROR: {e}")

        return "\n\n".join(results)
