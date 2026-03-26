"""Update propositie links in email templates to new UTM parameters."""

import re

from django.db import migrations

# New canonical URLs per doelgroep
NEW_URLS = {
    "zzp": "https://www.fenofin.nl/propositie/?utm_source=mailing&utm_medium=email&utm_campaign=zzp_propositie_maart2026",
    "kantoor": "https://www.fenofin.nl/propositie/kantoor/?utm_source=mailing&utm_medium=email&utm_campaign=kantoren_demo_maart2026",
    "bouw": "https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&utm_medium=email&utm_campaign=bouw_en_techniek_maart2026",
}

# HTML-escaped variants (& → &amp;)
NEW_URLS_HTML = {k: v.replace("&", "&amp;") for k, v in NEW_URLS.items()}

# Patterns to match old URLs (capture optional anchor like #administratie)
OLD_PATTERNS = {
    "zzp": re.compile(
        r"https://www\.fenofin\.nl/propositie/(?:klant/)?\?utm_source=(?:email|mailing)(?:&(?:amp;)?)[^\s\"<>]*?(?=#|\s|\"|\<|$)"
    ),
    "kantoor": re.compile(
        r"https://www\.fenofin\.nl/propositie/kantoor/\?utm_source=(?:email|mailing)(?:&(?:amp;)?)[^\s\"<>#]*"
    ),
    "bouw": re.compile(
        r"https://www\.fenofin\.nl/propositie/bouw-en-techniek/\?utm_source=(?:email|mailing)(?:&(?:amp;)?)[^\s\"<>#]*(#[a-z-]+)?"
    ),
}

TEMPLATE_MAPPING = {
    "klant-zzp-dga": "zzp",
    "administratiekantoren": "kantoor",
    "administratiekantoren-demo": "kantoor",
    "bouwbedrijven": "bouw",
}


def update_links(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    for slug, url_key in TEMPLATE_MAPPING.items():
        tpl = ResponseTemplate.objects.filter(slug=slug).first()
        if not tpl:
            continue

        new_url = NEW_URLS[url_key]
        new_url_html = NEW_URLS_HTML[url_key]
        pattern = OLD_PATTERNS[url_key]

        for field_name in ("body", "html_template"):
            content = getattr(tpl, field_name, "") or ""
            if not content:
                continue

            # For bouw templates: preserve anchor links
            if url_key == "bouw":
                def bouw_replacer(m):
                    anchor = m.group(1) or ""
                    # Use HTML-escaped version if the matched URL had &amp;
                    if "&amp;" in m.group(0):
                        return new_url_html + anchor
                    return new_url + anchor
                content = pattern.sub(bouw_replacer, content)
            else:
                # Simple replacement: use HTML-escaped version where appropriate
                def replacer(m):
                    if "&amp;" in m.group(0):
                        return new_url_html
                    return new_url
                content = pattern.sub(replacer, content)

            setattr(tpl, field_name, content)

        tpl.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0053_update_bouwbedrijven_template"),
    ]

    operations = [
        migrations.RunPython(update_links, noop),
    ]
