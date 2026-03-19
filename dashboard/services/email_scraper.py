import logging
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Common contact page paths to check
CONTACT_PATHS = [
    "/contact",
    "/contact/",
    "/contactus",
    "/contact-us",
    "/contact-us/",
    "/over-ons",
    "/over-ons/",
    "/about",
    "/about/",
    "/about-us",
    "/impressum",
    "/kontakt",
    "/team",
    "/team/",
    "/ons-team",
    "/ons-team/",
]

# Email pattern — matches common email addresses
EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
)

# Addresses to skip (generic/useless)
BLACKLIST_PATTERNS = {
    "example.com",
    "example.org",
    "sentry.io",
    "wixpress.com",
    "googleapis.com",
    "googleusercontent.com",
    "w3.org",
    "schema.org",
    "facebook.com",
    "twitter.com",
    "instagram.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "nl,en;q=0.9",
}

# Name labels commonly found near contact person names (Dutch + English)
NAME_LABELS = [
    "eigenaar", "owner", "directeur", "director", "oprichter", "founder",
    "contactpersoon", "contact person", "contact", "manager", "ceo",
    "managing director", "partner", "accountant", "adviseur", "advisor",
]

# Words that are NOT names — to filter false positives
NON_NAME_WORDS = {
    "de", "het", "van", "voor", "met", "een", "ons", "onze", "wij", "zij",
    "the", "and", "our", "we", "you", "info", "contact", "home", "about",
    "over", "meer", "lees", "read", "more", "telefoon", "phone", "email",
    "adres", "address", "login", "menu", "search", "zoeken", "nieuw",
    "welkom", "welcome", "diensten", "services", "producten", "products",
    "copyright", "privacy", "cookies", "disclaimer", "voorwaarden",
    "mobiel", "whatsapp", "fax", "e-mail", "postbus", "postcode",
    "kvk", "btw", "iban", "bic", "openingstijden", "bereikbaar",
    "bereikbaarheid",
}


@dataclass
class ScrapeResult:
    """Result of scraping a website for contact info."""
    email: str | None = None
    contact_first_name: str | None = None
    contact_last_name: str | None = None


def _is_valid_email(email: str) -> bool:
    """Filter out obviously invalid or blacklisted emails."""
    email = email.lower().strip()
    if len(email) > 254:
        return False
    domain = email.split("@", 1)[-1]
    for bl in BLACKLIST_PATTERNS:
        if bl in domain:
            return False
    # Skip image file extensions mistakenly matched
    if domain.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
        return False
    return True


def _extract_emails_from_html(html: str) -> set[str]:
    """Extract email addresses from HTML content."""
    emails = set()

    # 1. Extract from mailto: links
    soup = BeautifulSoup(html, "html.parser")
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("mailto:"):
            raw = href[7:].split("?")[0].strip()
            if EMAIL_RE.fullmatch(raw) and _is_valid_email(raw):
                emails.add(raw.lower())

    # 2. Extract from visible text and raw HTML
    text = soup.get_text(separator=" ")
    for match in EMAIL_RE.findall(text):
        if _is_valid_email(match):
            emails.add(match.lower())

    # 3. Also check raw HTML (some emails hidden in attributes/JS)
    for match in EMAIL_RE.findall(html):
        if _is_valid_email(match):
            emails.add(match.lower())

    return emails


def _is_likely_name(word: str) -> bool:
    """Check if a word looks like a proper name (capitalized, not a common word)."""
    if not word or len(word) < 2:
        return False
    if word.lower() in NON_NAME_WORDS:
        return False
    # Must start with uppercase
    if not word[0].isupper():
        return False
    # Rest should be letters (allow hyphens for double names like Anne-Marie)
    if not re.match(r"^[A-ZÀ-Ž][a-zà-ž]+(?:-[A-ZÀ-Ž][a-zà-ž]+)?$", word):
        return False
    return True


def _extract_name_near_email(soup: BeautifulSoup, email: str) -> tuple[str | None, str | None]:
    """Try to find a person's name near an email address in the HTML.

    Looks for patterns like:
    - "Jan de Vries - info@bedrijf.nl"
    - A heading or strong tag near the email
    - Structured data (vcard, schema.org)
    """
    # Strategy 1: Look for structured data (schema.org Person, vcard)
    first, last = _extract_name_from_structured_data(soup)
    if first or last:
        return first, last

    # Strategy 2: Find the email in text and look at surrounding context
    first, last = _extract_name_near_email_text(soup, email)
    if first or last:
        return first, last

    # Strategy 3: Look for common patterns in headings/team sections
    first, last = _extract_name_from_team_section(soup)
    if first or last:
        return first, last

    return None, None


def _extract_name_from_structured_data(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Extract name from schema.org or vcard structured data."""
    # Schema.org JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type", "")
                if t in ("Person", "LocalBusiness", "Organization"):
                    # Person has givenName/familyName
                    given = item.get("givenName", "")
                    family = item.get("familyName", "")
                    if given or family:
                        return given or None, family or None
                    # Or a "name" that might be a person
                    name = item.get("contactPoint", {}).get("name", "") if isinstance(item.get("contactPoint"), dict) else ""
                    if name:
                        parts = name.strip().split()
                        if 2 <= len(parts) <= 4:
                            return parts[0], " ".join(parts[1:])
                # Check employee/founder
                for key in ("founder", "employee", "author"):
                    person = item.get(key)
                    if isinstance(person, dict):
                        given = person.get("givenName", "")
                        family = person.get("familyName", "")
                        if given or family:
                            return given or None, family or None
                        name = person.get("name", "")
                        if name:
                            parts = name.strip().split()
                            if 2 <= len(parts) <= 4:
                                return parts[0], " ".join(parts[1:])
        except (json.JSONDecodeError, AttributeError, TypeError):
            continue

    # vcard microformat
    vcard = soup.find(class_="vcard") or soup.find(class_="h-card")
    if vcard:
        fn = vcard.find(class_="fn") or vcard.find(class_="p-name")
        if fn:
            parts = fn.get_text(strip=True).split()
            if 2 <= len(parts) <= 4:
                return parts[0], " ".join(parts[1:])

    return None, None


def _extract_name_near_email_text(soup: BeautifulSoup, email: str) -> tuple[str | None, str | None]:
    """Look for person names in text near the email address."""
    # Find all text nodes containing the email
    email_lower = email.lower()

    for element in soup.find_all(string=re.compile(re.escape(email_lower), re.IGNORECASE)):
        # Check the parent and siblings for name-like text
        parent = element.parent
        if not parent:
            continue

        # Walk up a few levels to find context
        for _ in range(3):
            if parent is None:
                break
            context_text = parent.get_text(separator=" ", strip=True)

            # Look for "Name - email" or "Name | email" patterns
            name = _extract_name_from_context(context_text, email)
            if name:
                return name

            # Also check sibling elements (name might be in a heading above)
            for sibling in parent.find_previous_siblings(["h1", "h2", "h3", "h4", "h5", "strong", "b", "p"], limit=3):
                text = sibling.get_text(strip=True)
                parts = text.split()
                if 2 <= len(parts) <= 4 and all(_is_likely_name(p) or p.lower() in ("van", "de", "den", "der", "het", "ter", "ten") for p in parts):
                    return parts[0], " ".join(parts[1:])

            parent = parent.parent

    return None, None


def _extract_name_from_context(text: str, email: str) -> tuple[str | None, str | None] | None:
    """Extract a name from text that also contains an email address."""
    # Remove the email from the text
    clean = text.replace(email, "").replace(email.lower(), "")

    # Common separators
    for sep in ["-", "–", "—", "|", ":", "·", "•", ","]:
        clean = clean.replace(sep, " ")

    # Remove common labels
    for label in NAME_LABELS:
        clean = re.sub(re.escape(label), " ", clean, flags=re.IGNORECASE)

    # Also remove phone numbers
    clean = re.sub(r"[\+\d\s\-\(\)]{8,}", " ", clean)

    # Clean up whitespace
    clean = " ".join(clean.split()).strip()

    if not clean:
        return None

    # Try to find a sequence of 2-4 capitalized words
    words = clean.split()
    name_parts = []
    # Dutch tussenvoegsels (infixes like "van", "de", "den")
    tussenvoegsels = {"van", "de", "den", "der", "het", "ter", "ten", "in", "'t"}

    for word in words:
        if _is_likely_name(word) or (name_parts and word.lower() in tussenvoegsels):
            name_parts.append(word)
        else:
            if len(name_parts) >= 2:
                break
            name_parts = []

    if len(name_parts) >= 2:
        return name_parts[0], " ".join(name_parts[1:])

    return None


def _extract_name_from_team_section(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Look for names in team/about sections — take the first (likely owner/director)."""
    # Look for role-related labels near names
    for label in NAME_LABELS[:8]:  # Focus on owner/director/founder
        pattern = re.compile(re.escape(label), re.IGNORECASE)
        for el in soup.find_all(string=pattern):
            parent = el.parent
            if not parent:
                continue
            # Check siblings and nearby elements
            for sibling in [parent] + list(parent.find_next_siblings(limit=3)) + list(parent.find_previous_siblings(limit=3)):
                text = sibling.get_text(strip=True) if hasattr(sibling, "get_text") else str(sibling).strip()
                # Remove the label itself
                text = re.sub(pattern, "", text).strip(" :,-–—|")
                words = text.split()
                tussenvoegsels = {"van", "de", "den", "der", "het", "ter", "ten"}
                name_words = [w for w in words if _is_likely_name(w) or w.lower() in tussenvoegsels]
                if 2 <= len(name_words) <= 4:
                    return name_words[0], " ".join(name_words[1:])

    return None, None


def _fetch_page(url: str, timeout: int = 10) -> str | None:
    """Fetch a page and return HTML or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
            return resp.text
    except requests.RequestException:
        pass
    return None


def scrape_contact_info(website_url: str) -> ScrapeResult:
    """Scrape a website for email and contact person name.

    Checks the homepage first, then common contact pages.
    Returns a ScrapeResult with email, first_name, last_name.
    """
    result = ScrapeResult()

    if not website_url:
        return result

    # Normalise URL
    if not website_url.startswith(("http://", "https://")):
        website_url = "https://" + website_url

    parsed = urlparse(website_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    pages_checked = []

    # 1. Try the homepage (or provided URL)
    logger.info("Contact scrape: checking %s", website_url)
    html = _fetch_page(website_url)
    if html:
        pages_checked.append((website_url, html))
        soup = BeautifulSoup(html, "html.parser")
        emails = _extract_emails_from_html(html)
        if emails:
            result.email = _pick_best_email(emails)
            first, last = _extract_name_near_email(soup, result.email)
            if first or last:
                result.contact_first_name = first
                result.contact_last_name = last
                return result

    # 2. Try common contact pages
    for path in CONTACT_PATHS:
        contact_url = urljoin(base_url, path)
        if contact_url == website_url:
            continue
        html = _fetch_page(contact_url)
        if html:
            pages_checked.append((contact_url, html))
            soup = BeautifulSoup(html, "html.parser")
            emails = _extract_emails_from_html(html)

            if emails:
                best_email = _pick_best_email(emails)
                if not result.email:
                    result.email = best_email

                first, last = _extract_name_near_email(soup, best_email)
                if first or last:
                    result.contact_first_name = first
                    result.contact_last_name = last
                    logger.info("Contact found on %s: %s %s", contact_url, first, last)
                    return result

            # Even without email, look for names on contact/team pages
            if not result.contact_first_name:
                first, last = _extract_name_from_team_section(soup)
                if first or last:
                    result.contact_first_name = first
                    result.contact_last_name = last

    # 3. If we still don't have a name, re-check all fetched pages for structured data
    if not result.contact_first_name:
        for url, html in pages_checked:
            soup = BeautifulSoup(html, "html.parser")
            first, last = _extract_name_from_structured_data(soup)
            if first or last:
                result.contact_first_name = first
                result.contact_last_name = last
                break

    if result.email or result.contact_first_name:
        logger.info("Scrape result for %s: email=%s, name=%s %s",
                     website_url, result.email, result.contact_first_name, result.contact_last_name)
    else:
        logger.info("No contact info found for %s", website_url)

    return result


def scrape_email(website_url: str) -> str | None:
    """Convenience wrapper — scrape only the email address."""
    return scrape_contact_info(website_url).email


def _pick_best_email(emails: set[str]) -> str:
    """Pick the most useful email from a set.

    Prefers info@, contact@, hello@, etc. over personal addresses.
    """
    priority_prefixes = ["info", "contact", "hello", "hallo", "office", "admin", "mail"]
    for prefix in priority_prefixes:
        for email in sorted(emails):
            if email.startswith(prefix + "@"):
                return email
    # Return first alphabetically
    return sorted(emails)[0]
