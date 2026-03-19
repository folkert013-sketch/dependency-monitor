import re

import requests
from bs4 import BeautifulSoup
from crewai.tools import BaseTool

from ._url_validation import is_allowed_url


class ArticleContentExtractorTool(BaseTool):
    name: str = "Article Content Extractor"
    description: str = (
        "Haalt de volledige artikelinhoud op van een URL. "
        "Werkt met overheids-, nieuws- en vakbladsites. "
        "Input: een volledige URL van een artikel. "
        "Returns: titel, publicatiedatum en schone tekst (max 8000 tekens)."
    )

    ALLOWED_DOMAINS: list = [
        # Overheid
        "belastingdienst.nl",
        "rijksoverheid.nl",
        "kvk.nl",
        "ondernemersplein.nl",
        "rvo.nl",
        "uwv.nl",
        "overheid.nl",
        "svb.nl",
        "government.nl",
        # Vakbladen & nieuws
        "accountant.nl",
        "taxlive.nl",
        "rendement.nl",
        "nu.nl",
        "nos.nl",
        "fd.nl",
        "mkbservicedesk.nl",
        "mkb-nederland.nl",
        "zzp-nederland.nl",
        "ondernemersplein.kvk.nl",
        "fiscaalconsult.nl",
        "taxence.nl",
        "pwc.nl",
        "deloitte.nl",
        "ey.com",
        "kpmg.nl",
    ]

    def _run(self, url: str) -> str:
        if not is_allowed_url(url, self.ALLOWED_DOMAINS):
            return (
                f"ERROR: URL '{url}' is geen toegestane bron. "
                f"Toegestaan: {', '.join(self.ALLOWED_DOMAINS[:10])}..."
            )

        try:
            resp = requests.get(url, timeout=20, headers={
                "User-Agent": "Mozilla/5.0 (compatible; FenoFinMonitor/1.0)"
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise
            for tag in soup.find_all(["nav", "footer", "script", "style", "aside", "header"]):
                tag.decompose()

            # Extract title
            title = ""
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"]
            elif soup.find("h1"):
                title = soup.find("h1").get_text(strip=True)
            elif soup.title:
                title = soup.title.get_text(strip=True)

            # Extract publication date
            pub_date = ""
            for meta_name in ["article:published_time", "og:article:published_time", "date", "pubdate"]:
                meta = soup.find("meta", property=meta_name) or soup.find("meta", attrs={"name": meta_name})
                if meta and meta.get("content"):
                    pub_date = meta["content"][:10]
                    break
            if not pub_date:
                time_tag = soup.find("time")
                if time_tag and time_tag.get("datetime"):
                    pub_date = time_tag["datetime"][:10]

            # Smart content extraction: try semantic selectors first
            content = None
            for selector in [
                {"name": "article"},
                {"attrs": {"role": "main"}},
                {"name": "main"},
                {"attrs": {"class": re.compile(r"article|post|content|entry", re.I)}},
                {"attrs": {"id": re.compile(r"article|post|content|main", re.I)}},
            ]:
                found = soup.find(**selector)
                if found:
                    text = found.get_text(separator="\n", strip=True)
                    if len(text) > 100:
                        content = text
                        break

            if not content:
                content = soup.get_text(separator="\n", strip=True)

            content = content[:8000]

            parts = [f"Bron: {url}"]
            if title:
                parts.append(f"Titel: {title}")
            if pub_date:
                parts.append(f"Publicatiedatum: {pub_date}")
            parts.append(f"--- Artikelinhoud ---\n{content}\n--- Einde artikelinhoud ---")

            return "\n".join(parts)

        except requests.RequestException as e:
            return f"ERROR: Kon artikel niet ophalen: {url} — {e}"
