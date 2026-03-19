from urllib.parse import urlparse


def is_allowed_url(url: str, allowed_domains: list[str]) -> bool:
    """Check if a URL's hostname matches one of the allowed domains.

    Uses proper hostname parsing instead of substring matching to prevent
    bypasses like ``https://belastingdienst.nl.evil.com/``.
    """
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if not hostname or parsed.scheme not in ("http", "https"):
        return False
    return any(
        hostname == domain or hostname.endswith("." + domain)
        for domain in allowed_domains
    )
