import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool

from ._url_validation import is_allowed_url


class GovernmentSiteFetcherTool(BaseTool):
    name: str = "Government Site Fetcher"
    description: str = (
        "Fetcht content van Nederlandse overheidswebsites "
        "(belastingdienst.nl, rijksoverheid.nl, kvk.nl, ondernemersplein.nl, rvo.nl, uwv.nl, wetten.overheid.nl, svb.nl). "
        "Input: een volledige URL van een overheidspagina. "
        "Returns: schone tekst van de pagina (max 5000 tekens)."
    )

    def _run(self, url: str) -> str:
        allowed_domains = [
            "belastingdienst.nl",
            "rijksoverheid.nl",
            "kvk.nl",
            "ondernemersplein.kvk.nl",
            "ondernemersplein.nl",
            "rvo.nl",
            "uwv.nl",
            "overheid.nl",
            "svb.nl",
            "rechtspraak.nl",
            "government.nl",
        ]

        if not is_allowed_url(url, allowed_domains):
            return f"ERROR: URL '{url}' is geen bekende overheidswebsite. Toegestaan: {', '.join(allowed_domains)}"

        try:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (compatible; FenoFinMonitor/1.0)"
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove navigation, footer, scripts
            for tag in soup.find_all(["nav", "footer", "script", "style", "aside"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)[:5000]

            return (
                f"Bron: {url}\n"
                f"--- Pagina-inhoud ---\n"
                f"{text}\n"
                f"--- Einde pagina-inhoud ---"
            )
        except requests.RequestException as e:
            return f"ERROR: Kon pagina niet ophalen: {url} — {e}"
