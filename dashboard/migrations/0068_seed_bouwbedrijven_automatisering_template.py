"""Seed short automation-focused outreach template for bouwbedrijven."""

from django.db import migrations

BODY = """{aanhef} {achternaam},

Mijn naam is Folkert Feenstra \u2014 ik combineer accountancy met ICT.
Ik help bedrijven zoals {bedrijfsnaam} met het automatiseren van de financi\u00eble administratie en het bouwen van slimme koppelingen.

Zijn er zaken die u zou willen automatiseren?

Denk aan:
\u2713 Automatische factuurverwerking en boekingen
\u2713 Koppelingen tussen uw systemen en de boekhouding
\u2713 Tools op maat voor uw specifieke werkprocessen

Ik bouw snel, denk mee vanuit de administratie, en lever werkende oplossingen.

Benieuwd wat er mogelijk is?
Bekijk de propositie: https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&utm_medium=email&utm_campaign=bouw_automatisering_maart2026

Met vriendelijke groet,

Folkert Feenstra
FenoFin B.V. | Zuidlaren
https://www.linkedin.com/in/folkert-feenstra-a78665b3/
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FenoFin</title>
</head>
<body style="margin:0;padding:0;background-color:#f8fafc;font-family:'Segoe UI',Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8fafc;">
<tr><td align="center" style="padding:32px 12px;">

<!-- Main container -->
<table role="presentation" width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);">

  <!-- Header -->
  <tr>
    <td style="padding:28px 40px 20px;border-bottom:1px solid #e0e7ff;">
      <span style="font-size:22px;font-weight:700;color:#4f46e5;letter-spacing:-0.5px;">FenoFin</span>
    </td>
  </tr>

  <!-- Intro -->
  <tr>
    <td style="padding:32px 40px 16px;">
      <p style="margin:0 0 20px;color:#1a1a2e;font-size:15px;line-height:1.75;">
        {aanhef} {achternaam},
      </p>
      <p style="margin:0;color:#374151;font-size:15px;line-height:1.75;">
        Mijn naam is Folkert Feenstra &#8212; ik combineer <strong style="color:#1a1a2e;">accountancy</strong> met <strong style="color:#1a1a2e;">ICT</strong>.
        Ik help bedrijven zoals {bedrijfsnaam} met het automatiseren van de financi&#235;le administratie en het bouwen van slimme koppelingen.
      </p>
    </td>
  </tr>

  <!-- Drie voorbeelden heading -->
  <tr>
    <td style="padding:8px 40px 12px;">
      <p style="margin:0;color:#6b7280;font-size:14px;">Denk aan:</p>
    </td>
  </tr>

  <!-- Voorbeeld 1 -->
  <tr>
    <td style="padding:0 40px 10px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:top;color:#4f46e5;font-size:16px;font-weight:700;">&#10003;</td>
                <td>
                  <span style="color:#1a1a2e;font-size:14px;font-weight:700;">Automatische factuurverwerking</span>
                  <span style="color:#374151;font-size:14px;"> &#8212; facturen en boekingen automatisch verwerkt</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Voorbeeld 2 -->
  <tr>
    <td style="padding:0 40px 10px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:top;color:#4f46e5;font-size:16px;font-weight:700;">&#10003;</td>
                <td>
                  <span style="color:#1a1a2e;font-size:14px;font-weight:700;">Koppelingen</span>
                  <span style="color:#374151;font-size:14px;"> &#8212; uw systemen verbonden met de boekhouding</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Voorbeeld 3 -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:top;color:#4f46e5;font-size:16px;font-weight:700;">&#10003;</td>
                <td>
                  <span style="color:#1a1a2e;font-size:14px;font-weight:700;">Tools op maat</span>
                  <span style="color:#374151;font-size:14px;"> &#8212; voor uw specifieke werkprocessen</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Afsluiter -->
  <tr>
    <td style="padding:0 40px 24px;">
      <p style="margin:0;color:#374151;font-size:15px;line-height:1.75;">
        Ik bouw snel, denk mee vanuit de administratie, en lever werkende oplossingen.
      </p>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="padding:0 40px 24px;" align="center">
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#4f46e5;border-radius:8px;">
            <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_automatisering_maart2026"
               style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:0.2px;">
              Bekijk de propositie &#8594;
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Signature -->
  <tr>
    <td style="padding:8px 40px 20px;">
      <p style="margin:0 0 4px;color:#374151;font-size:15px;line-height:1.7;">Met vriendelijke groet,</p>
      <p style="margin:12px 0 0;color:#1a1a2e;font-size:15px;font-weight:700;">Folkert Feenstra</p>
      <p style="margin:2px 0 0;color:#6b7280;font-size:13px;">FenoFin B.V. | Zuidlaren</p>
      <p style="margin:6px 0 0;">
        <a href="https://www.linkedin.com/in/folkert-feenstra-a78665b3/" style="color:#4f46e5;font-size:13px;text-decoration:none;">LinkedIn &#8594;</a>
      </p>
    </td>
  </tr>

  <!-- Divider -->
  <tr>
    <td style="padding:0 40px;">
      <hr style="border:none;border-top:1px solid #e0e7ff;margin:0;">
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:20px 40px 24px;text-align:center;">
      <p style="margin:0 0 4px;color:#9ca3af;font-size:12px;">
        FenoFin B.V. &middot; <a href="https://www.fenofin.nl" style="color:#4f46e5;text-decoration:none;">fenofin.nl</a>
      </p>
      <p style="margin:0;color:#c4c7cc;font-size:11px;">
        U ontvangt deze e-mail omdat wij denken dat onze diensten relevant zijn voor uw bedrijf.
      </p>
    </td>
  </tr>

</table>
<!-- /Main container -->

</td></tr>
</table>
</body>
</html>"""


def seed_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    # Reuse category from existing bouwbedrijven template
    category = None
    try:
        existing = ResponseTemplate.objects.get(slug="bouwbedrijven")
        category = existing.category
    except ResponseTemplate.DoesNotExist:
        pass

    ResponseTemplate.objects.update_or_create(
        slug="bouwbedrijven-automatisering",
        defaults={
            "name": "Bouwbedrijven \u2014 Automatisering",
            "subject": "Automatisering van uw administratie bij {bedrijfsnaam}",
            "body": BODY.strip(),
            "html_template": HTML_TEMPLATE.strip(),
            "is_starred": False,
            "category": category,
            "order": 0,
        },
    )


def remove_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    ResponseTemplate.objects.filter(slug="bouwbedrijven-automatisering").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0067_seed_bouwbedrijven_kort_template"),
    ]

    operations = [
        migrations.RunPython(seed_template, remove_template),
    ]
