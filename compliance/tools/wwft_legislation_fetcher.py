import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


class WWFTLegislationFetcherTool(BaseTool):
    name: str = "WWFT Legislation Fetcher"
    description: str = (
        "Doorzoekt publieke bronnen op actuele WWFT wet- en regelgeving. "
        "Input: een zoekterm (bijv. 'WWFT wijziging', 'UBO-register', 'Wwft identificatie'). "
        "Returns: relevante wetsartikelen, richtlijnen en publicaties."
    )

    SOURCES: list = [
        {
            "name": "Wetten.overheid.nl",
            "url": "https://wetten.overheid.nl",
            "search_url": "https://wetten.overheid.nl/zoeken?q={query}&c=wet",
        },
        {
            "name": "Bureau Financieel Toezicht (BFT)",
            "url": "https://www.bureauft.nl",
            "search_url": "https://www.bureauft.nl/?s={query}",
        },
        {
            "name": "FIU-Nederland",
            "url": "https://www.fiu-nederland.nl",
            "search_url": "https://www.fiu-nederland.nl/zoeken/?q={query}",
        },
        {
            "name": "De Nederlandsche Bank (DNB)",
            "url": "https://www.dnb.nl",
            "search_url": "https://www.dnb.nl/zoeken/?q={query}&type=alles",
        },
        {
            "name": "Rijksoverheid - Witwassen",
            "url": "https://www.rijksoverheid.nl",
            "search_url": "https://www.rijksoverheid.nl/zoeken?trefwoord={query}",
        },
    ]

    def _run(self, search_term: str) -> str:
        results = []

        for source in self.SOURCES:
            search_url = source["search_url"].format(
                query=requests.utils.quote(search_term)
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
                    results.append(
                        f"Bron: {source['name']}\n"
                        f"  Geen resultaten gevonden voor '{search_term}'\n"
                        f"  URL: {search_url}"
                    )

            except requests.RequestException as e:
                results.append(f"Bron: {source['name']}\n  ERROR: {e}")

        return "\n\n".join(results)
