import re
from urllib.parse import quote


def rewrite_links(html, tracking_token, base_url):
    """Rewrite href URLs to local tracking redirects."""
    def _replace_href(match):
        url = match.group(1)
        if url.startswith(("mailto:", "tel:", "#")):
            return match.group(0)
        tracked = f"{base_url}/t/c/{tracking_token}/?url={quote(url, safe='')}"
        return f'href="{tracked}"'

    return re.sub(r'href="(https?://[^"]+)"', _replace_href, html, flags=re.IGNORECASE)


def inject_tracking_pixel(html, tracking_token, base_url):
    """Insert a 1x1 tracking pixel before </body>."""
    pixel = (
        f'<img src="{base_url}/t/o/{tracking_token}/" '
        f'width="1" height="1" style="display:none" alt="" />'
    )
    if "</body>" in html.lower():
        return re.sub(r"</body>", f"{pixel}</body>", html, count=1, flags=re.IGNORECASE)
    return html + pixel


def prepare_tracked_email(html, tracking_token, base_url):
    """Rewrite links and inject tracking pixel."""
    html = rewrite_links(html, tracking_token, base_url)
    html = inject_tracking_pixel(html, tracking_token, base_url)
    return html
