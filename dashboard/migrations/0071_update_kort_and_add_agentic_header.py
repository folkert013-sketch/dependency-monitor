"""Update bouwbedrijven-kort with correct pillars and add Agentic Accounting header to both templates."""

from django.db import migrations

KORT_BODY = """{aanhef} {achternaam},

Mijn naam is Folkert Feenstra \u2014 afgestudeerd Praktijkopleiding Accountancy met een sterke affiniteit voor ICT.

Uw vaste contactpersoon voor de financi\u00eble administratie en IT-zaken bij {bedrijfsnaam} \u2014 geen fulltime medewerker nodig, wel iemand die het betrouwbaar regelt of reviewt.

Drie pijlers van ondersteuning:

\u2713 Administratie & VPB \u2014 boekhouding, BTW en vennootschapsbelasting
\u2713 Automatisering & Tools \u2014 data ontsluiten, koppelingen en maatwerk tools
\u2713 ICT & Netwerkbeheer \u2014 internet, wifi en website-onderhoud

Periodieke review \u2014 niet voor een hele werkweek, wel doorlopend inzetbaar.

Bekijk de volledige propositie: https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&utm_medium=email&utm_campaign=bouw_kort_maart2026

Met vriendelijke groet,

Folkert Feenstra
FenoFin B.V. | Zuidlaren
https://www.linkedin.com/in/folkert-feenstra-a78665b3/
"""

KORT_HTML = """<!DOCTYPE html>
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
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <span style="font-size:22px;font-weight:700;color:#4f46e5;letter-spacing:-0.5px;">FenoFin</span>
          </td>
          <td style="text-align:right;">
            <span style="color:#6b7280;font-size:13px;font-style:italic;">Agentic Accounting</span>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Intro -->
  <tr>
    <td style="padding:32px 40px 16px;">
      <p style="margin:0 0 20px;color:#1a1a2e;font-size:15px;line-height:1.75;">
        {aanhef} {achternaam},
      </p>
      <p style="margin:0 0 16px;color:#374151;font-size:15px;line-height:1.75;">
        Mijn naam is Folkert Feenstra &#8212; afgestudeerd
        <strong style="color:#1a1a2e;">Praktijkopleiding Accountancy</strong> met een sterke
        <strong style="color:#1a1a2e;">affiniteit voor ICT</strong>.
      </p>
      <p style="margin:0;color:#374151;font-size:15px;line-height:1.75;">
        Uw vaste contactpersoon voor de financi&#235;le administratie en IT-zaken bij {bedrijfsnaam} &#8212;
        geen fulltime medewerker nodig, wel iemand die het betrouwbaar regelt of reviewt.
      </p>
    </td>
  </tr>

  <!-- Drie pijlers heading -->
  <tr>
    <td style="padding:8px 40px 16px;">
      <p style="margin:0;color:#1a1a2e;font-size:16px;font-weight:700;">Drie pijlers van ondersteuning</p>
    </td>
  </tr>

  <!-- Pijler 1: Administratie & VPB -->
  <tr>
    <td style="padding:0 40px 10px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:top;color:#4f46e5;font-size:16px;font-weight:700;">&#10003;</td>
                <td>
                  <span style="color:#1a1a2e;font-size:14px;font-weight:700;">Administratie &amp; VPB</span>
                  <span style="color:#374151;font-size:14px;"> &#8212; boekhouding, BTW en vennootschapsbelasting</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Pijler 2: Automatisering & Tools -->
  <tr>
    <td style="padding:0 40px 10px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:top;color:#4f46e5;font-size:16px;font-weight:700;">&#10003;</td>
                <td>
                  <span style="color:#1a1a2e;font-size:14px;font-weight:700;">Automatisering &amp; Tools</span>
                  <span style="color:#374151;font-size:14px;"> &#8212; data ontsluiten, koppelingen en maatwerk tools</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Pijler 3: ICT & Netwerkbeheer -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;">
        <tr>
          <td style="padding:14px 18px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:top;color:#4f46e5;font-size:16px;font-weight:700;">&#10003;</td>
                <td>
                  <span style="color:#1a1a2e;font-size:14px;font-weight:700;">ICT &amp; Netwerkbeheer</span>
                  <span style="color:#374151;font-size:14px;"> &#8212; internet, wifi en website-onderhoud</span>
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
      <p style="margin:0;color:#374151;font-size:14px;line-height:1.75;font-style:italic;">
        Periodieke review &#8212; niet voor een hele werkweek, wel doorlopend inzetbaar.
      </p>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="padding:0 40px 24px;" align="center">
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#4f46e5;border-radius:8px;">
            <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_kort_maart2026"
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

# Header snippet to find and replace in the automatisering template
OLD_HEADER = '<span style="font-size:22px;font-weight:700;color:#4f46e5;letter-spacing:-0.5px;">FenoFin</span>'

NEW_HEADER = """<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <span style="font-size:22px;font-weight:700;color:#4f46e5;letter-spacing:-0.5px;">FenoFin</span>
          </td>
          <td style="text-align:right;">
            <span style="color:#6b7280;font-size:13px;font-style:italic;">Agentic Accounting</span>
          </td>
        </tr>
      </table>"""


def update_templates(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    # 1. Update bouwbedrijven-kort: full body + html replacement
    kort = ResponseTemplate.objects.filter(slug="bouwbedrijven-kort").first()
    if kort:
        kort.body = KORT_BODY.strip()
        kort.html_template = KORT_HTML.strip()
        kort.save()

    # 2. Update bouwbedrijven-automatisering: add Agentic Accounting header
    auto = ResponseTemplate.objects.filter(slug="bouwbedrijven-automatisering").first()
    if auto and auto.html_template and OLD_HEADER in auto.html_template:
        auto.html_template = auto.html_template.replace(OLD_HEADER, NEW_HEADER)
        auto.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0070_seed_linkedin_templates"),
    ]

    operations = [
        migrations.RunPython(update_templates, noop),
    ]
