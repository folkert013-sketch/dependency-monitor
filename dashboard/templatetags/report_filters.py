import markdown2
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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
    icons = {
        "critical": "🔴",
        "warning": "🟠",
        "info": "🟢",
    }
    return icons.get(severity, "⚪")


@register.filter
def render_markdown(text):
    if not text:
        return ""
    return mark_safe(markdown2.markdown(text, extras=["fenced-code-blocks", "tables"]))
