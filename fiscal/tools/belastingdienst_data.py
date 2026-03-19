import re

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool

from ._url_validation import is_allowed_url


class BelastingdienstStructuredDataTool(BaseTool):
    name: str = "Belastingdienst Structured Data"
    description: str = (
        "Haalt gestructureerde gegevens op van belastingdienst.nl — tabellen, tarieven en "
        "bedragen in een overzichtelijk format. "
        "Input: een topic (bijv. 'btw-tarieven', 'ib-schijven', 'vpb', 'zzp', 'box3', 'kor') "
        "of een volledige belastingdienst.nl URL. "
        "Returns: gestructureerde data met tabellen en lijsten (max 10000 tekens)."
    )

    TOPIC_URLS: dict = {
        "btw-tarieven": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_berekenen_aan_klanten/btw_tarief/",
        "btw": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/btw_berekenen_aan_klanten/btw_tarief/",
        "ib-schijven": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/",
        "ib": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/",
        "vpb": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/vennootschapsbelasting/",
        "zzp": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/ondernemen/ondernemers/",
        "zelfstandigenaftrek": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/winst/inkomstenbelasting/inkomstenbelasting_voor_ondernemers/zelfstandigenaftrek/",
        "box3": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/vermogen_en_aanmerkelijk_belang/",
        "kor": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/btw/hoe_werkt_de_btw/kleineondernemersregeling/",
        "loonbelasting": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/zakelijk/personeel_en_loon/",
        "arbeidskorting": "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/inkomstenbelasting/heffingskortingen_boxen_tarieven/heffingskortingen/arbeidskorting/",
    }

    def _run(self, topic: str) -> str:
        topic_lower = topic.strip().lower()

        # If it's a full URL, use it directly
        if topic_lower.startswith("http"):
            url = topic.strip()
            if not is_allowed_url(url, ["belastingdienst.nl"]):
                return "ERROR: Alleen belastingdienst.nl URLs zijn toegestaan."
        elif topic_lower in self.TOPIC_URLS:
            url = self.TOPIC_URLS[topic_lower]
        else:
            # Fallback: search on belastingdienst.nl
            search_url = f"https://www.belastingdienst.nl/wps/wcm/connect/nl/zoeken/zoeken?zkt={requests.utils.quote(topic)}"
            return self._fetch_and_structure(search_url, topic)

        return self._fetch_and_structure(url, topic)

    def _fetch_and_structure(self, url: str, topic: str) -> str:
        try:
            resp = requests.get(url, timeout=20, headers={
                "User-Agent": "Mozilla/5.0 (compatible; FenoFinMonitor/1.0)"
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise
            for tag in soup.find_all(["nav", "footer", "script", "style", "aside", "header"]):
                tag.decompose()

            parts = [f"Bron: {url}", f"Topic: {topic}", ""]

            # 1. Extract tables
            tables = soup.find_all("table")
            if tables:
                parts.append("=== TABELLEN ===")
                for i, table in enumerate(tables[:5], 1):
                    parts.append(f"\nTabel {i}:")
                    rows = table.find_all("tr")
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        cell_texts = [c.get_text(strip=True) for c in cells]
                        if any(cell_texts):
                            parts.append("| " + " | ".join(cell_texts) + " |")

            # 2. Extract definition lists (dt/dd pairs)
            dl_items = soup.find_all("dl")
            if dl_items:
                parts.append("\n=== DEFINITIES ===")
                for dl in dl_items[:3]:
                    dts = dl.find_all("dt")
                    dds = dl.find_all("dd")
                    for dt, dd in zip(dts, dds):
                        parts.append(f"- {dt.get_text(strip=True)}: {dd.get_text(strip=True)}")

            # 3. Extract lists with amounts/percentages
            amount_pattern = re.compile(r'[€$]\s*[\d.,]+|[\d.,]+\s*%')
            lists_with_amounts = []
            for li in soup.find_all("li"):
                text = li.get_text(strip=True)
                if amount_pattern.search(text) and len(text) < 300:
                    lists_with_amounts.append(f"- {text}")

            if lists_with_amounts:
                parts.append("\n=== BEDRAGEN EN PERCENTAGES ===")
                parts.extend(lists_with_amounts[:20])

            # 4. If no structured data found, fall back to main content
            if len(parts) <= 3:
                main = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"})
                if main:
                    text = main.get_text(separator="\n", strip=True)
                else:
                    text = soup.get_text(separator="\n", strip=True)
                parts.append("=== PAGINA-INHOUD ===")
                parts.append(text)

            output = "\n".join(parts)
            return output[:10000]

        except requests.RequestException as e:
            return f"ERROR: Kon pagina niet ophalen: {url} — {e}"
