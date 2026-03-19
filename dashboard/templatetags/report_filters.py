import re

import bleach
import markdown2
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = [
    "a", "abbr", "acronym", "b", "blockquote", "br", "code", "dd", "del",
    "div", "dl", "dt", "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr",
    "i", "img", "ins", "li", "ol", "p", "pre", "small", "span", "strong",
    "sub", "sup", "svg", "path", "table", "tbody", "td", "tfoot", "th",
    "thead", "tr", "ul",
]

ALLOWED_ATTRIBUTES = {
    "*": ["class", "id"],
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "svg": ["class", "fill", "stroke", "viewBox", "xmlns", "width", "height"],
    "path": ["d", "fill", "stroke", "stroke-linecap", "stroke-linejoin", "stroke-width"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
}


def _sanitize_html(html: str) -> str:
    """Sanitize HTML using bleach to prevent XSS attacks."""
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )


CALLOUT_ICONS = {
    "TIP": '<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>',
    "WARNING": '<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>',
    "DEADLINE": '<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
    "ACTION": '<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>',
    "INFO": '<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
}

CALLOUT_STYLES = {
    "TIP": "border-emerald-400 bg-emerald-50 text-emerald-800",
    "WARNING": "border-amber-400 bg-amber-50 text-amber-800",
    "DEADLINE": "border-red-400 bg-red-50 text-red-800",
    "ACTION": "border-blue-400 bg-blue-50 text-blue-800",
    "INFO": "border-purple-400 bg-purple-50 text-purple-800",
}

CALLOUT_TITLE_STYLES = {
    "TIP": "text-emerald-900",
    "WARNING": "text-amber-900",
    "DEADLINE": "text-red-900",
    "ACTION": "text-blue-900",
    "INFO": "text-purple-900",
}


def _process_callouts(text: str) -> str:
    """Convert GitHub-style blockquote callouts to styled HTML divs.

    Syntax:
        > [!TIP] Optional title
        > Content line 1
        > Content line 2

    Supported types: TIP, WARNING, DEADLINE, ACTION, INFO
    """
    # Pattern matches callout blocks: > [!TYPE] title\n> content lines
    pattern = re.compile(
        r'^(?:> \[!(TIP|WARNING|DEADLINE|ACTION|INFO)\]\s*(.*)\n)'  # header line
        r'((?:> .*\n?)*)',  # content lines
        re.MULTILINE | re.IGNORECASE,
    )

    def _replace_callout(match):
        callout_type = match.group(1).upper()
        title = escape(match.group(2).strip())
        content_lines = match.group(3)

        # Strip leading '> ' from each content line
        content = escape("\n".join(
            line.lstrip("> ").rstrip() for line in content_lines.strip().split("\n")
        ).strip())

        style = CALLOUT_STYLES.get(callout_type, CALLOUT_STYLES["INFO"])
        title_style = CALLOUT_TITLE_STYLES.get(callout_type, CALLOUT_TITLE_STYLES["INFO"])
        icon = CALLOUT_ICONS.get(callout_type, CALLOUT_ICONS["INFO"])

        title_html = f'<span class="font-semibold {title_style}">{title}</span>' if title else ""

        return (
            f'<div class="callout callout-{callout_type.lower()} not-prose border-l-4 {style} rounded-r-xl p-4 my-4">'
            f'<div class="flex items-start gap-3">'
            f'{icon}'
            f'<div class="flex-1">'
            f'{title_html}'
            f'<div class="mt-1 text-sm leading-relaxed">{content}</div>'
            f'</div></div></div>\n\n'
        )

    return pattern.sub(_replace_callout, text)


@register.filter
def intcomma(value):
    """Format an integer with thousand separators (dots for NL locale)."""
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value


@register.filter
def status_color(status):
    colors = {
        "critical": "red",
        "warning": "amber",
        "ok": "emerald",
    }
    return colors.get(status, "gray")


@register.filter
def status_bg(status):
    bgs = {
        "critical": "bg-red-100 text-red-800",
        "warning": "bg-amber-100 text-amber-800",
        "ok": "bg-emerald-100 text-emerald-800",
    }
    return bgs.get(status, "bg-gray-100 text-gray-800")


@register.filter
def severity_icon(severity):
    """Return SVG icon with aria-label for accessibility (N4: replaces emoji-only indicators)."""
    icon_map = {
        "critical": (
            '<span class="inline-flex items-center gap-1" role="img" aria-label="Kritiek">'
            '<svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">'
            '<circle cx="10" cy="10" r="8"/></svg>'
            '<span class="sr-only">Kritiek</span></span>'
        ),
        "warning": (
            '<span class="inline-flex items-center gap-1" role="img" aria-label="Waarschuwing">'
            '<svg class="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">'
            '<circle cx="10" cy="10" r="8"/></svg>'
            '<span class="sr-only">Waarschuwing</span></span>'
        ),
        "info": (
            '<span class="inline-flex items-center gap-1" role="img" aria-label="Informatie">'
            '<svg class="w-4 h-4 text-emerald-500" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">'
            '<circle cx="10" cy="10" r="8"/></svg>'
            '<span class="sr-only">Informatie</span></span>'
        ),
    }
    return mark_safe(icon_map.get(severity, '<span aria-label="Onbekend">\u26aa</span>'))


def _preprocess_llm_markdown(text: str) -> str:
    """Preprocess LLM output to ensure proper markdown rendering.

    LLMs often produce text with single newlines where markdown requires
    double newlines for paragraph breaks, and write section headings as
    plain short lines without ``##`` prefix.
    """
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")
    result: list[str] = []
    in_code_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track fenced code blocks — never modify content inside them
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue
        if in_code_block:
            result.append(line)
            continue

        # Skip already-formatted markdown headings
        if stripped.startswith("#"):
            result.append(line)
            continue

        # Detect heading-like lines: short, non-empty, no trailing sentence
        # punctuation, followed by a longer content line.
        is_heading_candidate = (
            stripped
            and len(stripped) <= 80
            and not stripped.endswith((".", ":", ",", ";", "!", "?"))
            and not stripped.startswith(("-", "*", "1.", ">", "|"))
        )
        if is_heading_candidate:
            # Look at the next non-empty line
            next_line = ""
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    next_line = lines[j].strip()
                    break
            # If the next content line is substantially longer, treat as heading
            if next_line and len(next_line) > len(stripped) * 1.5 and len(next_line) > 40:
                result.append(f"## {stripped}")
                continue

        result.append(line)

    # Ensure blank lines between paragraphs: insert a blank line between
    # two consecutive non-empty, non-special lines.
    spaced: list[str] = []
    for i, line in enumerate(result):
        spaced.append(line)
        if i < len(result) - 1:
            cur = line.strip()
            nxt = result[i + 1].strip()
            if (
                cur and nxt
                and not cur.startswith(("#", "-", "*", ">", "|", "```"))
                and not nxt.startswith(("#", "-", "*", ">", "|", "```"))
            ):
                spaced.append("")

    return "\n".join(spaced)


@register.filter
def render_markdown(text):
    if not text:
        return ""
    # Strip stray closing tags that LLMs sometimes produce
    text = re.sub(r'</(?:div|section|article|main|body|html)>\s*$', '', text.strip())
    # Normalise LLM output so markdown can parse it properly
    text = _preprocess_llm_markdown(text)
    # Process callout syntax before markdown rendering
    text = _process_callouts(text)
    html = markdown2.markdown(text, extras=[
        "fenced-code-blocks",
        "tables",
        "header-ids",
        "strike",
        "task_list",
        "cuddled-lists",
        "target-blank-links",
    ])
    html = _sanitize_html(html)
    return mark_safe(html)


@register.filter
def clean_html(text):
    """Render text that may already contain HTML from LLM output."""
    if not text:
        return ""
    # Strip stray closing tags
    text = re.sub(r'</(?:div|section|article|main|body|html)>\s*$', '', text.strip())
    # Strip wrapping quotes if present
    text = text.strip('"').strip("'")
    text = _sanitize_html(text)
    return mark_safe(text)


@register.filter
def category_color(category):
    colors = {
        "btw": "blue",
        "ib": "purple",
        "vpb": "amber",
        "loonbelasting": "rose",
        "subsidies": "emerald",
        "deadlines": "red",
        "algemeen": "gray",
    }
    return colors.get(category, "gray")


@register.filter
def category_bg(category):
    bgs = {
        "btw": "bg-blue-100 text-blue-800",
        "ib": "bg-purple-100 text-purple-800",
        "vpb": "bg-amber-100 text-amber-800",
        "loonbelasting": "bg-rose-100 text-rose-800",
        "subsidies": "bg-emerald-100 text-emerald-800",
        "deadlines": "bg-red-100 text-red-800",
        "algemeen": "bg-gray-100 text-gray-800",
    }
    return bgs.get(category, "bg-gray-100 text-gray-800")


@register.filter
def article_status_bg(status):
    bgs = {
        "draft": "bg-yellow-100 text-yellow-800",
        "published": "bg-emerald-100 text-emerald-800",
        "archived": "bg-gray-100 text-gray-800",
    }
    return bgs.get(status, "bg-gray-100 text-gray-800")


@register.filter
def reading_time(text):
    """Geschatte leestijd in minuten."""
    if not text:
        return 1
    return max(1, round(len(text.split()) / 200))


@register.filter
def contains_pk(queryset, pk):
    """Check if a queryset contains an object with the given pk."""
    try:
        return queryset.filter(pk=pk).exists()
    except (AttributeError, TypeError, ValueError):
        return False
