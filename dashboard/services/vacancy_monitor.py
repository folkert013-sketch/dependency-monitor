"""
Vacancy Monitor Service — fetches job vacancies from Jooble, Adzuna, and CareerJet.

All sources are free:
- Jooble: free API key at https://jooble.org/api/about
- Adzuna: free account at https://developer.adzuna.com/signup
- CareerJet: free affiliate ID at https://www.careerjet.com/partners/api
"""

import hashlib
import logging
import re
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_TIMEOUT = 20
_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class VacancyMonitorService:
    """Fetches vacancies from multiple Dutch job sources."""

    CATEGORIES = {
        "financieel": {
            "label": "Financieel administratie",
            "keywords": [
                "financieel", "financiële", "administratie", "boekhouder",
                "accountant", "fiscaal", "controller", "financien",
                "salarisadministratie", "debiteuren", "crediteuren",
                "loonadministratie", "belasting",
            ],
        },
        "data_analyse": {
            "label": "Data-analyse",
            "keywords": [
                "data", "analist", "analyse", "analytics",
                "business intelligence", "power bi", "data engineer",
                "data scientist", "tableau", "dashboard",
            ],
        },
        "ict": {
            "label": "ICT en netwerken",
            "keywords": [
                "ict", "software", "developer", "ontwikkelaar",
                "netwerk", "systeem", "devops", "cloud", "security",
                "beheerder", "programmeur", "informatica", "it ",
                "full stack", "frontend", "backend", "engineer",
            ],
        },
        "zzp_admin": {
            "label": "ZZP Administratie / Accountancy",
            "keywords": [
                "zzp", "freelance", "interim", "zelfstandig", "opdracht",
                "accountant", "boekhouder", "administratie", "controller",
                "fiscaal", "jaarrekening", "salarisadministratie",
            ],
        },
        "automatisering": {
            "label": "Automatisering / Digitalisering",
            "keywords": [
                "automatisering", "digitalisering", "proces", "workflow",
                "excel", "power bi", "rapportage", "migratie",
                "implementatie", "erp", "exact", "twinfield", "afas",
                "boekhoud", "koppeling", "api",
            ],
        },
    }

    NOORD_NEDERLAND_LOCATIONS = ["Groningen", "Friesland", "Drenthe"]

    # ─── Jooble API ──────────────────────────────────────────────

    def search_jooble(self, keywords: str, location: str = "", page: int = 1) -> list[dict]:
        """
        Fetch vacancies from Jooble API.

        Requires JOOBLE_API_KEY in settings. Free at jooble.org/api/about.
        Supports Dutch city names like "Groningen", "Zuidlaren", etc.
        """
        api_key = getattr(settings, "JOOBLE_API_KEY", "")
        if not api_key:
            logger.debug("Jooble API key not configured, skipping")
            return []

        url = f"https://jooble.org/api/{api_key}"
        # Append "Netherlands" to location to avoid US results for Dutch city names
        jooble_location = f"{location}, Netherlands" if location else "Netherlands"
        payload = {
            "keywords": keywords,
            "location": jooble_location,
            "page": str(page),
        }

        try:
            resp = requests.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": _USER_AGENT,
                },
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning("Jooble API request failed: %s", e)
            return []
        except ValueError:
            logger.warning("Jooble API returned invalid JSON")
            return []

        results = []
        for job in data.get("jobs", []):
            title = (job.get("title") or "").strip()
            company = (job.get("company") or "").strip()
            link = (job.get("link") or "").strip()
            loc = (job.get("location") or "").strip()
            salary = (job.get("salary") or "").strip()
            snippet = (job.get("snippet") or "").strip()
            updated = (job.get("updated") or "").strip()

            external_id = f"jooble-{hashlib.md5(link.encode()).hexdigest()}" if link else ""

            published_date = None
            if updated:
                try:
                    published_date = datetime.fromisoformat(
                        updated.replace("Z", "+00:00")
                    ).date()
                except ValueError:
                    pass

            if title and external_id:
                results.append({
                    "external_id": external_id,
                    "title": _clean_html(title),
                    "company_name": company,
                    "location": loc,
                    "description": _clean_html(snippet),
                    "salary": salary,
                    "source_url": link,
                    "source": "jooble",
                    "published_date": published_date,
                })

        return results

    # ─── Adzuna API ──────────────────────────────────────────────

    def search_adzuna(self, keywords: str, location: str = "", page: int = 1) -> list[dict]:
        """
        Fetch vacancies from Adzuna API (Netherlands).

        Requires ADZUNA_APP_ID + ADZUNA_APP_KEY. Free at developer.adzuna.com/signup.
        """
        app_id = getattr(settings, "ADZUNA_APP_ID", "")
        app_key = getattr(settings, "ADZUNA_APP_KEY", "")
        if not app_id or not app_key:
            logger.debug("Adzuna API credentials not configured, skipping")
            return []

        url = f"https://api.adzuna.com/v1/api/jobs/nl/search/{page}"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": keywords,
            "results_per_page": 50,
        }
        if location:
            params["where"] = location

        try:
            resp = requests.get(
                url,
                params=params,
                headers={"User-Agent": _USER_AGENT},
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning("Adzuna API request failed: %s", e)
            return []
        except ValueError:
            logger.warning("Adzuna API returned invalid JSON")
            return []

        results = []
        for job in data.get("results", []):
            title = (job.get("title") or "").strip()
            company = ""
            company_data = job.get("company") or {}
            if isinstance(company_data, dict):
                company = (company_data.get("display_name") or "").strip()

            loc_data = job.get("location") or {}
            loc = ""
            if isinstance(loc_data, dict):
                loc_parts = loc_data.get("display_name", "").split(",")
                loc = loc_parts[0].strip() if loc_parts else ""

            link = (job.get("redirect_url") or "").strip()
            description = (job.get("description") or "").strip()
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            salary = ""
            if salary_min and salary_max:
                salary = f"\u20ac{int(salary_min):,} - \u20ac{int(salary_max):,}"
            elif salary_min:
                salary = f"vanaf \u20ac{int(salary_min):,}"

            adzuna_id = job.get("id", "")
            external_id = f"adzuna-{adzuna_id}" if adzuna_id else ""

            created = (job.get("created") or "").strip()
            published_date = None
            if created:
                try:
                    published_date = datetime.fromisoformat(
                        created.replace("Z", "+00:00")
                    ).date()
                except ValueError:
                    pass

            if title and external_id:
                results.append({
                    "external_id": external_id,
                    "title": _clean_html(title),
                    "company_name": company,
                    "location": loc,
                    "description": _clean_html(description)[:500],
                    "salary": salary,
                    "source_url": link,
                    "source": "adzuna",
                    "published_date": published_date,
                })

        return results

    # ─── CareerJet API ───────────────────────────────────────────

    def search_careerjet(self, keywords: str, location: str = "", page: int = 1) -> list[dict]:
        """
        Fetch vacancies from CareerJet API (Dutch locale).

        Requires CAREERJET_AFFID in settings. Free at careerjet.com/partners/api.
        Supports Dutch cities and regions.
        """
        affid = getattr(settings, "CAREERJET_AFFID", "")
        if not affid:
            logger.debug("CareerJet affiliate ID not configured, skipping")
            return []

        # CareerJet requires HTTP (not HTTPS), user_ip, user_agent, and Referer header
        url = "http://public.api.careerjet.net/search"
        params = {
            "affid": affid,
            "keywords": keywords,
            "location": location,
            "locale_code": "nl_NL",
            "page": page,
            "pagesize": 50,
            "sort": "date",
            "user_ip": "127.0.0.1",
            "user_agent": _USER_AGENT,
        }

        try:
            resp = requests.get(
                url,
                params=params,
                headers={"User-Agent": _USER_AGENT, "Referer": "https://fenofin.nl"},
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning("CareerJet API request failed: %s", e)
            return []
        except ValueError:
            logger.warning("CareerJet API returned invalid JSON")
            return []

        results = []
        for job in data.get("jobs", []):
            title = (job.get("title") or "").strip()
            company = (job.get("company") or "").strip()
            loc = (job.get("locations") or "").strip()
            link = (job.get("url") or "").strip()
            description = (job.get("description") or "").strip()
            salary = (job.get("salary") or "").strip()
            date_str = (job.get("date") or "").strip()

            external_id = f"careerjet-{hashlib.md5(link.encode()).hexdigest()}" if link else ""

            published_date = None
            if date_str:
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%a, %d %b %Y"):
                    try:
                        published_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue

            if title and external_id:
                results.append({
                    "external_id": external_id,
                    "title": _clean_html(title),
                    "company_name": company,
                    "location": loc,
                    "description": _clean_html(description)[:500],
                    "salary": salary,
                    "source_url": link,
                    "source": "careerjet",
                    "published_date": published_date,
                })

        return results

    # ─── Combined search ─────────────────────────────────────────

    def search_all(
        self, query: str, location: str = "", sources: list[str] | None = None
    ) -> list[dict]:
        """
        Search all configured sources. Returns combined, deduplicated results.

        sources: list of source names, e.g. ["jooble", "adzuna", "careerjet"].
                 If None, uses all available sources.
        """
        if sources is None:
            sources = ["jooble", "adzuna", "careerjet"]

        all_results = []
        seen_ids = set()

        for source in sources:
            try:
                if source == "jooble":
                    results = self.search_jooble(query, location)
                elif source == "adzuna":
                    results = self.search_adzuna(query, location)
                elif source == "careerjet":
                    results = self.search_careerjet(query, location)
                else:
                    continue
            except Exception:
                logger.exception("Error searching %s", source)
                continue

            for r in results:
                eid = r.get("external_id", "")
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    if not r.get("category"):
                        r["category"] = self.match_category(
                            r.get("title", ""), r.get("description", "")
                        )
                    r["relevance_score"] = self.relevance_score(
                        r.get("title", ""), r.get("description", "")
                    )
                    all_results.append(r)

        return all_results

    # ─── Categorization ──────────────────────────────────────────

    def match_category(self, title: str, description: str = "") -> str:
        """Match a vacancy title/description against our categories."""
        text = f"{title} {description}".lower()
        best_match = ""
        best_score = 0

        for cat_key, cat_info in self.CATEGORIES.items():
            score = sum(1 for kw in cat_info["keywords"] if kw in text)
            if score > best_score:
                best_score = score
                best_match = cat_key

        return best_match if best_score > 0 else ""

    # ─── Relevance scoring ─────────────────────────────────────────

    def relevance_score(self, title: str, description: str = "") -> int:
        """
        Score 0-100: how relevant is this vacancy for Folkert's ZZP profile.

        Scoring:
        - ZZP/freelance signals: up to 30 pts
        - Accountancy/admin match: up to 30 pts
        - ICT/automation match: up to 30 pts
        - Noord-Nederland location: 10 pts
        """
        text = f"{title} {description}".lower()
        score = 0

        # ZZP/freelance signals (+30 max)
        zzp_terms = ["zzp", "freelance", "interim", "zelfstandig", "opdracht",
                     "tijdelijk", "inhuur", "detachering", "contractor"]
        score += min(30, sum(10 for t in zzp_terms if t in text))

        # Accountancy/admin match (+30 max)
        admin_terms = ["accountant", "boekhouder", "administratie", "controller",
                       "fiscaal", "jaarrekening", "salarisadministratie",
                       "financieel", "financiële", "vpb", "btw"]
        score += min(30, sum(10 for t in admin_terms if t in text))

        # ICT/automation match (+30 max)
        ict_terms = ["automatisering", "digitalisering", "software", "excel",
                     "power bi", "exact", "twinfield", "afas", "erp", "data",
                     "koppeling", "api", "implementatie", "migratie", "workflow"]
        score += min(30, sum(10 for t in ict_terms if t in text))

        # Noord-Nederland location bonus (+10)
        nl_locations = ["groningen", "drenthe", "friesland", "assen",
                        "zuidlaren", "haren", "hoogezand", "veendam",
                        "stadskanaal", "emmen", "hoogeveen", "meppel",
                        "leeuwarden", "heerenveen", "sneek"]
        if any(loc in text for loc in nl_locations):
            score += 10

        return min(100, score)

    # ─── Company extraction ──────────────────────────────────────

    def extract_companies(self, vacancies: list[dict]) -> list[dict]:
        """
        Group vacancies by company name.

        Returns list of dicts sorted by vacancy_count descending:
        {name, location, vacancy_count, categories, vacancies}
        """
        companies = {}
        for v in vacancies:
            company = v.get("company_name", "").strip()
            if not company:
                continue

            key = company.lower()
            if key not in companies:
                companies[key] = {
                    "name": company,
                    "location": v.get("location", ""),
                    "vacancy_count": 0,
                    "categories": set(),
                    "vacancies": [],
                    "_scores": [],
                }

            companies[key]["vacancy_count"] += 1
            cat = v.get("category", "")
            if cat:
                companies[key]["categories"].add(cat)
            companies[key]["vacancies"].append(v)
            companies[key]["_scores"].append(v.get("relevance_score", 0))

        result = list(companies.values())
        for c in result:
            c["categories"] = sorted(c["categories"])
            scores = c.pop("_scores", [])
            c["avg_relevance"] = round(sum(scores) / len(scores)) if scores else 0
            c["max_relevance"] = max(scores) if scores else 0
        # Sort by max relevance score (most relevant first), then by vacancy count
        result.sort(key=lambda c: (c["max_relevance"], c["vacancy_count"]), reverse=True)

        return result


# ─── Helpers ─────────────────────────────────────────────────────

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _clean_html(text: str) -> str:
    """Strip HTML tags from text."""
    return _HTML_TAG_RE.sub("", text).strip()
