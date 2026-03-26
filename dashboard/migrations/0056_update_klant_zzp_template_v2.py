"""Update klant ZZP/DGA email template to match website propositie."""

from django.db import migrations

BODY = """{aanhef} {achternaam},

Mijn naam is Folkert Feenstra, afgestudeerd AA-accountant (MKB) en oprichter van FenoFin. Met FenoFin bied ik AI-ge\u00efntegreerd boekhouden speciaal voor ZZP\u2019ers en DGA\u2019s.

Ik wil u graag laten zien wat FenoFin voor {bedrijfsnaam} kan betekenen. Hieronder vindt u onze unieke propositie.

\u2713 WhatsApp AI Chat \u2014 Cockpit (uniek aan FenoFin)

Uw boekhouding bedienen via WhatsApp \u2014 geen app, geen inloggen:
\u2022 Verkoopfactuur aanmaken en direct versturen
\u2022 \u201cWelke facturen staan nog open?\u201d
\u2022 \u201cWat is mijn omzet deze maand?\u201d

\u2713 Automatische factuurverwerking

\u2022 WhatsApp of e-mail \u2014 stuur uw inkoopfactuur naar FenoFin
\u2022 AI herkent leverancier, leest bedrag en BTW, boekt automatisch in
\u2022 Banktransacties worden \u2019s nachts automatisch gematcht
Geen gedoe met scannen of uploaden \u2014 gewoon doorsturen.

\u2713 Wat u krijgt

\u2022 Altijd up-to-date boekhouding zonder zelf in te loggen
\u2022 Persoonlijke AA-accountant die meekijkt
\u2022 AI-gedreven inzichten in uw cijfers via WhatsApp

Ik laat het u graag zien. Ontdek wat AI-ge\u00efntegreerd boekhouden voor {bedrijfsnaam} kan betekenen.

Bekijk de volledige propositie: https://www.fenofin.nl/propositie/?utm_source=mailing&utm_medium=email&utm_campaign=zzp_propositie_maart2026

Met vriendelijke groet,

Folkert Feenstra
FenoFin B.V. | Zuidlaren
f.feenstra@fenofin.nl | www.fenofin.nl
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
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <span style="font-size:22px;font-weight:700;color:#4f46e5;letter-spacing:-0.5px;">FenoFin</span>
          </td>
          <td align="right">
            <span style="font-size:12px;color:#9ca3af;">Agentic | Accounting</span>
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
        Mijn naam is Folkert Feenstra, afgestudeerd <strong style="color:#1a1a2e;">AA-accountant (MKB)</strong>
        en oprichter van FenoFin. Met FenoFin bied ik <strong style="color:#1a1a2e;">AI-ge&#239;ntegreerd boekhouden</strong>
        speciaal voor ZZP&#8217;ers en DGA&#8217;s.
      </p>
      <p style="margin:0 0 8px;color:#374151;font-size:15px;line-height:1.75;">
        Ik wil u graag laten zien wat FenoFin voor {bedrijfsnaam} kan betekenen.
        Hieronder vindt u onze unieke propositie.
      </p>
    </td>
  </tr>

  <!-- USP banner -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:linear-gradient(135deg,#4f46e5 0%,#6366f1 100%);border-radius:10px;padding:14px 20px;text-align:center;">
            <p style="margin:0;color:#ffffff;font-size:15px;font-weight:600;letter-spacing:0.2px;">
              Geen app openen, geen inloggen &#8212; gewoon appen
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Dienst 1: WhatsApp Cockpit -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128172;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">WhatsApp AI Chat &#8212; Cockpit</span>
                  <span style="color:#6b7280;font-size:13px;"> &#8212; uniek aan FenoFin</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 8px;color:#374151;font-size:14px;line-height:1.6;">
              Uw boekhouding bedienen via WhatsApp &#8212; geen app, geen inloggen:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Verkoopfactuur</strong> &#8212; aanmaken en direct versturen
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  &#8220;Welke facturen staan nog open?&#8221;
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  &#8220;Wat is mijn omzet deze maand?&#8221;
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Dienst 2: Factuurverwerking -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128196;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">Automatische factuurverwerking</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>WhatsApp of e-mail</strong> &#8212; stuur uw inkoopfactuur naar FenoFin
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>AI herkent</strong> &#8212; leverancier, bedrag en BTW, boekt automatisch in
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Banktransacties</strong> &#8212; worden &#8217;s nachts automatisch gematcht
                </td>
              </tr>
            </table>
            <p style="margin:12px 0 0;color:#6b7280;font-size:13px;font-style:italic;">
              Geen gedoe met scannen of uploaden &#8212; gewoon doorsturen.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Dienst 3: Wat u krijgt -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#127919;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">Wat u krijgt</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Altijd up-to-date</strong> &#8212; boekhouding zonder zelf in te loggen
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Persoonlijke AA-accountant</strong> &#8212; die meekijkt
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>AI-gedreven inzichten</strong> &#8212; in uw cijfers via WhatsApp
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="padding:0 40px 12px;" align="center">
      <p style="margin:0 0 16px;color:#374151;font-size:15px;line-height:1.7;text-align:center;">
        Ik laat het u graag zien. Ontdek wat AI-ge&#239;ntegreerd boekhouden voor {bedrijfsnaam} kan betekenen.
      </p>
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#4f46e5;border-radius:8px;">
            <a href="mailto:f.feenstra@fenofin.nl?subject=Kennismaking%20FenoFin%20%E2%80%94%20{bedrijfsnaam}"
               style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:0.2px;">
              Vrijblijvend kennismaken &#8594;
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Propositie link -->
  <tr>
    <td style="padding:12px 40px 8px;" align="center">
      <a href="https://www.fenofin.nl/propositie/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=zzp_propositie_maart2026"
         style="color:#4f46e5;font-size:14px;text-decoration:none;font-weight:500;">
        Bekijk de volledige propositie op fenofin.nl &#8594;
      </a>
    </td>
  </tr>

  <!-- Signature -->
  <tr>
    <td style="padding:28px 40px 20px;">
      <p style="margin:0 0 4px;color:#374151;font-size:15px;line-height:1.7;">Met vriendelijke groet,</p>
      <p style="margin:12px 0 0;color:#1a1a2e;font-size:15px;font-weight:700;">Folkert Feenstra</p>
      <p style="margin:2px 0 0;color:#6b7280;font-size:13px;">AA-accountant (MKB) | Oprichter FenoFin</p>
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


def update_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    tpl = ResponseTemplate.objects.filter(slug="klant-zzp-dga").first()
    if not tpl:
        return
    tpl.body = BODY.strip()
    tpl.html_template = HTML_TEMPLATE.strip()
    tpl.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0055_update_bouwbedrijven_template_v2"),
    ]

    operations = [
        migrations.RunPython(update_template, noop),
    ]
