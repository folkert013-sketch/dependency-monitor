"""Update signature block in bouwbedrijven-kort and bouwbedrijven-automatisering templates."""

from django.db import migrations

OLD_BODY_SIGNATURE = (
    "Folkert Feenstra\n"
    "FenoFin B.V. | Zuidlaren\n"
    "https://www.linkedin.com/in/folkert-feenstra-a78665b3/"
)

NEW_BODY_SIGNATURE = (
    "Folkert Feenstra\n"
    "FenoFin B.V. | Zuidlaren\n"
    "f.feenstra@fenofin.nl | www.fenofin.nl"
)

OLD_HTML_SIGNATURE = """  <!-- Signature -->
  <tr>
    <td style="padding:8px 40px 20px;">
      <p style="margin:0 0 4px;color:#374151;font-size:15px;line-height:1.7;">Met vriendelijke groet,</p>
      <p style="margin:12px 0 0;color:#1a1a2e;font-size:15px;font-weight:700;">Folkert Feenstra</p>
      <p style="margin:2px 0 0;color:#6b7280;font-size:13px;">FenoFin B.V. | Zuidlaren</p>
      <p style="margin:6px 0 0;">
        <a href="https://www.linkedin.com/in/folkert-feenstra-a78665b3/" style="color:#4f46e5;font-size:13px;text-decoration:none;">LinkedIn &#8594;</a>
      </p>
    </td>
  </tr>"""

NEW_HTML_SIGNATURE = """  <!-- Signature -->
  <tr>
    <td style="padding:28px 40px 20px;">
      <p style="margin:0 0 4px;color:#374151;font-size:15px;line-height:1.7;">Met vriendelijke groet,</p>
      <p style="margin:12px 0 0;color:#1a1a2e;font-size:15px;font-weight:700;">Folkert Feenstra</p>
      <p style="margin:2px 0 0;color:#6b7280;font-size:13px;">FenoFin B.V. | Zuidlaren</p>
      <p style="margin:6px 0 0;color:#6b7280;font-size:13px;">
        <a href="mailto:f.feenstra@fenofin.nl" style="color:#4f46e5;text-decoration:none;">f.feenstra@fenofin.nl</a>
        &nbsp;&middot;&nbsp;
        <a href="https://www.fenofin.nl" style="color:#4f46e5;text-decoration:none;">www.fenofin.nl</a>
        &nbsp;&middot;&nbsp;
        <a href="https://wa.me/31612622344" style="color:#4f46e5;text-decoration:none;">WhatsApp</a>
        &nbsp;&middot;&nbsp;
        <a href="https://www.linkedin.com/in/folkert-feenstra-a78665b3/" style="color:#4f46e5;text-decoration:none;">LinkedIn</a>
      </p>
    </td>
  </tr>"""


def update_signatures(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    for slug in ("bouwbedrijven-kort", "bouwbedrijven-automatisering"):
        tpl = ResponseTemplate.objects.filter(slug=slug).first()
        if not tpl:
            continue

        changed = False

        if OLD_BODY_SIGNATURE in tpl.body:
            tpl.body = tpl.body.replace(OLD_BODY_SIGNATURE, NEW_BODY_SIGNATURE)
            changed = True

        if OLD_HTML_SIGNATURE in tpl.html_template:
            tpl.html_template = tpl.html_template.replace(
                OLD_HTML_SIGNATURE, NEW_HTML_SIGNATURE
            )
            changed = True

        if changed:
            tpl.save()


def revert_signatures(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    for slug in ("bouwbedrijven-kort", "bouwbedrijven-automatisering"):
        tpl = ResponseTemplate.objects.filter(slug=slug).first()
        if not tpl:
            continue

        changed = False

        if NEW_BODY_SIGNATURE in tpl.body:
            tpl.body = tpl.body.replace(NEW_BODY_SIGNATURE, OLD_BODY_SIGNATURE)
            changed = True

        if NEW_HTML_SIGNATURE in tpl.html_template:
            tpl.html_template = tpl.html_template.replace(
                NEW_HTML_SIGNATURE, OLD_HTML_SIGNATURE
            )
            changed = True

        if changed:
            tpl.save()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0068_seed_bouwbedrijven_automatisering_template"),
    ]

    operations = [
        migrations.RunPython(update_signatures, revert_signatures),
    ]
