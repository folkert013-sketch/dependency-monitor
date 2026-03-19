import re

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool


class FiscalNewsAggregatorTool(BaseTool):
    name: str = "Fiscal News Aggregator"
    description: str = (
        "Doorzoekt een breed scala aan Nederlandse fiscale nieuwsbronnen — vakbladen, "
        "nieuwssites en MKB-portals naast overheidssites. "
        "Input: zoekterm, optioneel met bronfilter via '|' "
        "(bijv. 'btw verhoging|vakbladen', 'zzp regelingen|mkb'). "
        "Brongroepen: overheid, vakbladen, nieuws, mkb. "
        "Returns: lijst van gevonden artikelen met titel, datum en URL."
    )

    SOURCE_GROUPS: dict = {
        "overheid": [
            {"name": "Rijksoverheid", "url": "https://www.rijksoverheid.nl", "search": "https://www.rijksoverheid.nl/zoeken?trefwoord={query}"},
            {"name": "Belastingdienst", "url": "https://www.belastingdienst.nl", "search": "https://www.belastingdienst.nl/wps/wcm/connect/nl/zoeken/zoeken?zkt={query}"},
        ],
        "vakbladen": [
            {"name": "Accountant.nl", "url": "https://www.accountant.nl", "search": "https://www.accountant.nl/zoeken/?q={query}"},
            {"name": "TaxLive", "url": "https://www.taxlive.nl", "search": "https://www.taxlive.nl/zoeken/?q={query}"},
            {"name": "Rendement.nl", "url": "https://www.rendement.nl", "search": "https://www.rendement.nl/zoeken?q={query}"},
        ],
        "nieuws": [
            {"name": "NU.nl Economie", "url": "https://www.nu.nl", "search": "https://www.nu.nl/zoeken/?q={query}&section=economie"},
            {"name": "NOS Economie", "url": "https://nos.nl", "search": "https://nos.nl/zoeken?q={query}"},
        ],
        "mkb": [
            {"name": "MKB Servicedesk", "url": "https://www.mkbservicedesk.nl", "search": "https://www.mkbservicedesk.nl/?s={query}"},
            {"name": "MKB-Nederland", "url": "https://www.mkb-nederland.nl", "search": "https://www.mkb-nederland.nl/?s={query}"},
            {"name": "KvK Ondernemersplein", "url": "https://ondernemersplein.kvk.nl", "search": "https://ondernemersplein.kvk.nl/zoeken/?query={query}"},
            {"name": "ZZP Nederland", "url": "https://www.zzp-nederland.nl", "search": "https://www.zzp-nederland.nl/?s={query}"},
        ],
    }

    def _run(self, input_str: str) -> str:
        # Parse input: "zoekterm|groep" or just "zoekterm"
        parts = input_str.split("|", 1)
        search_term = parts[0].strip()
        group_filter = parts[1].strip().lower() if len(parts) > 1 else None

        # Select source groups
        if group_filter:
            sources = []
            for group_name, group_sources in self.SOURCE_GROUPS.items():
                if group_filter in group_name:
                    sources.extend(group_sources)
            if not sources:
                available = ", ".join(self.SOURCE_GROUPS.keys())
                return f"Onbekende brongroep '{group_filter}'. Beschikbaar: {available}"
        else:
            sources = []
            for group_sources in self.SOURCE_GROUPS.values():
                sources.extend(group_sources)

        results = []

        for source in sources:
            search_url = source["search"].format(query=requests.utils.quote(search_term))
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

                        # Try to find a date near this link
                        pub_date = self._extract_nearby_date(link)
                        date_str = f" ({pub_date})" if pub_date else ""

                        articles.append(f"  - {title}{date_str}\n    URL: {href}")
                    if len(articles) >= 5:
                        break

                if articles:
                    results.append(f"Bron: {source['name']}\n" + "\n".join(articles))
                else:
                    results.append(f"Bron: {source['name']}\n  Geen resultaten voor '{search_term}'")

            except requests.RequestException as e:
                results.append(f"Bron: {source['name']}\n  ERROR: {e}")

        return "\n\n".join(results)

    @staticmethod
    def _extract_nearby_date(element) -> str:
        """Try to find a publication date near a link element."""
        # Check parent and siblings for time tags or date patterns
        parent = element.parent
        if not parent:
            return ""

        time_tag = parent.find("time")
        if time_tag:
            return time_tag.get("datetime", time_tag.get_text(strip=True))[:10]

        # Look for date patterns in parent text
        parent_text = parent.get_text(strip=True)
        date_match = re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2}', parent_text)
        if date_match:
            return date_match.group()

        return ""
