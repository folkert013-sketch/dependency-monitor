import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


class TaxNewsSearcherTool(BaseTool):
    name: str = "Tax News Searcher"
    description: str = (
        "Doorzoekt bekende Nederlandse fiscale nieuwsbronnen op recente ontwikkelingen. "
        "Input: een zoekterm (bijv. 'btw-verhoging', 'loonbelasting 2026', 'subsidie MKB'). "
        "Returns: lijst van relevante artikelen met titel, datum en URL."
    )

    SOURCES: list = [
        {
            "name": "Belastingdienst Nieuws",
            "url": "https://www.belastingdienst.nl/wps/wcm/connect/nl/home/home",
            "search_url": "https://www.belastingdienst.nl/wps/wcm/connect/nl/zoeken/zoeken?zkt={query}",
        },
        {
            "name": "Rijksoverheid Belastingen",
            "url": "https://www.rijksoverheid.nl/onderwerpen/belasting-betalen",
            "search_url": "https://www.rijksoverheid.nl/zoeken?trefwoord={query}",
        },
        {
            "name": "KvK Ondernemersplein",
            "url": "https://ondernemersplein.kvk.nl",
            "search_url": "https://ondernemersplein.kvk.nl/zoeken/?query={query}",
        },
        {
            "name": "Ondernemersplein.nl",
            "url": "https://www.ondernemersplein.nl",
            "search_url": "https://www.ondernemersplein.nl/zoeken/?query={query}",
        },
        {
            "name": "RVO",
            "url": "https://www.rvo.nl",
            "search_url": "https://www.rvo.nl/zoeken?search_api_fulltext={query}",
        },
        {
            "name": "UWV",
            "url": "https://www.uwv.nl",
            "search_url": "https://www.uwv.nl/zoeken?zoekterm={query}",
        },
    ]

    def _run(self, search_term: str) -> str:
        results = []

        for source in self.SOURCES:
            search_url = source["search_url"].format(query=requests.utils.quote(search_term))
            try:
                resp = requests.get(search_url, timeout=15, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; FenoFinMonitor/1.0)"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Try to find article/result links
                articles = []
                for link in soup.find_all("a", href=True):
                    title = link.get_text(strip=True)
                    href = link["href"]
                    if len(title) > 20 and len(title) < 200 and not href.startswith("#"):
                        if not href.startswith("http"):
                            base = source["url"].rstrip("/")
                            href = f"{base}/{href.lstrip('/')}"
                        articles.append(f"  - {title}\n    URL: {href}")
                    if len(articles) >= 5:
                        break

                if articles:
                    results.append(f"Bron: {source['name']}\n" + "\n".join(articles))
                else:
                    results.append(f"Bron: {source['name']}\n  Geen resultaten gevonden voor '{search_term}'")

            except requests.RequestException as e:
                results.append(f"Bron: {source['name']}\n  ERROR: {e}")

        return "\n\n".join(results)
