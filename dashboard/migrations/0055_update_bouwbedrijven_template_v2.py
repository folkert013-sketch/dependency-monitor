"""Update bouwbedrijven email template to match website propositie page."""

from django.db import migrations

BODY = """{aanhef} {achternaam},

Mijn naam is Folkert Feenstra, afgestudeerd Praktijkopleiding Accountancy met een sterke affiniteit voor ICT.

Uw vaste externe specialist voor de financi\u00eble administratie en IT-zaken bij {bedrijfsnaam} \u2014 geen fulltime medewerker nodig, wel iemand die het betrouwbaar regelt.

Drie diensten die uw bedrijf direct ondersteunen:

\u2713 Financi\u00eble administratie en automatisering
Ondersteuning bij uw administratie \u2014 in uw eigen pakket of via FenoFin:
\u2022 Doorlopen administratie \u2014 periodiek doorlopen en samenstellen van de jaarrekening
\u2022 FenoFin boekhouding \u2014 optioneel: ons AI-boekhoudsysteem met automatische factuurverwerking
\u2022 BTW-aangifte \u2014 ik verzorg de aangifte, ongeacht welk pakket u gebruikt
Neem alleen af wat u nodig heeft \u2014 volledig vrijblijvend.

\u2713 Aangifte VPB
Vennootschapsbelasting \u2014 indienen of als concept voorbereiden:
\u2022 Volledig indienen \u2014 ik stel de aangifte samen en dien deze in bij de Belastingdienst
\u2022 Concept aanleveren \u2014 ik bereid de aangifte voor, uw accountant dient in
\u2022 Persoonlijk overleg \u2014 afstemming over fiscale keuzes en optimalisatie
Flexibel: volledig uitbesteden of als concept laten voorbereiden.

\u2713 ICT en netwerkbeheer
Uw contactpersoon voor IT-zaken \u2014 geen dure IT-afdeling nodig:
\u2022 Internet en wifi \u2014 inrichten op kantoor, in de werkplaats of op locatie, inclusief netwerk en beveiliging
\u2022 Website-onderhoud \u2014 kleine aanpassingen, updates en hosting geregeld
\u2022 Vast aanspreekpunt \u2014 storing of vraag? U belt mij direct
Geen IT-afdeling nodig \u2014 u heeft een vaste contactpersoon.

E\u00e9n contactpersoon voor administratie en ICT \u2014 geen fulltime medewerker nodig.

Interesse in een vrijblijvend kennismakingsgesprek?
f.feenstra@fenofin.nl | 06-12622344

Bekijk de volledige propositie: https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&utm_medium=email&utm_campaign=bouw_en_techniek_maart2026

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
        Mijn naam is Folkert Feenstra, afgestudeerd
        <strong style="color:#1a1a2e;">Praktijkopleiding Accountancy</strong> met een sterke
        <strong style="color:#1a1a2e;">affiniteit voor ICT</strong>.
      </p>
      <p style="margin:0 0 8px;color:#374151;font-size:15px;line-height:1.75;">
        Uw vaste externe specialist voor de financi&#235;le administratie en IT-zaken bij {bedrijfsnaam} &#8212;
        geen fulltime medewerker nodig, wel iemand die het betrouwbaar regelt.
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
              E&#233;n aanspreekpunt &#8212; u belt &#233;&#233;n persoon voor administratie &#233;n ICT
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Drie diensten heading -->
  <tr>
    <td style="padding:0 40px 16px;">
      <p style="margin:0;color:#1a1a2e;font-size:16px;font-weight:700;">Drie diensten die uw bedrijf direct ondersteunen</p>
    </td>
  </tr>

  <!-- Dienst 1: Administratie -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128202;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">Financi&#235;le administratie</span>
                  <span style="color:#6b7280;font-size:13px;"> &#8212; facturen, BTW en boekhouding geregeld</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 8px;color:#374151;font-size:14px;line-height:1.6;">
              Ondersteuning bij uw administratie &#8212; in uw eigen pakket of via FenoFin:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Doorlopen administratie</strong> &#8212; periodiek doorlopen van uw administratie en samenstellen van de jaarrekening
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>FenoFin boekhouding</strong> &#8212; optioneel: gebruik ons AI-boekhoudsysteem met automatische factuurverwerking
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>BTW-aangifte</strong> &#8212; ik verzorg de aangifte, ongeacht welk pakket u gebruikt
                </td>
              </tr>
            </table>
            <p style="margin:12px 0 0;color:#6b7280;font-size:13px;font-style:italic;">
              Neem alleen af wat u nodig heeft &#8212; volledig vrijblijvend.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Dienst 2: VPB -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128209;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">Aangifte VPB</span>
                  <span style="color:#6b7280;font-size:13px;"> &#8212; indienen of als concept voorbereiden</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 8px;color:#374151;font-size:14px;line-height:1.6;">
              Vennootschapsbelasting &#8212; indienen of als concept voorbereiden:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Volledig indienen</strong> &#8212; ik stel de aangifte samen en dien deze in bij de Belastingdienst
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Concept aanleveren</strong> &#8212; ik bereid de aangifte voor, uw accountant dient in
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Persoonlijk overleg</strong> &#8212; afstemming over fiscale keuzes en optimalisatie
                </td>
              </tr>
            </table>
            <p style="margin:12px 0 0;color:#6b7280;font-size:13px;font-style:italic;">
              Flexibel: volledig uitbesteden of als concept laten voorbereiden.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Dienst 3: ICT -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128421;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">ICT &amp; Netwerkbeheer</span>
                  <span style="color:#6b7280;font-size:13px;"> &#8212; uw vaste IT-contactpersoon</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 8px;color:#374151;font-size:14px;line-height:1.6;">
              Uw contactpersoon voor IT-zaken &#8212; geen dure IT-afdeling nodig:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Internet en wifi</strong> &#8212; inrichten op kantoor, in de werkplaats of op locatie, inclusief netwerk en beveiliging
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Website-onderhoud</strong> &#8212; kleine aanpassingen, updates en hosting geregeld
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Vast aanspreekpunt</strong> &#8212; storing of vraag? U belt mij direct
                </td>
              </tr>
            </table>
            <p style="margin:12px 0 0;color:#6b7280;font-size:13px;font-style:italic;">
              Geen IT-afdeling nodig &#8212; u heeft een vaste contactpersoon.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Doelgroepen -->
  <tr>
    <td style="padding:0 40px 8px;">
      <p style="margin:0 0 12px;color:#1a1a2e;font-size:16px;font-weight:700;">Voor welk type bedrijf?</p>
    </td>
  </tr>
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="width:33%;padding:0 6px 0 0;vertical-align:top;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;overflow:hidden;">
              <tr><td style="background-color:#eef2ff;padding:10px 12px;text-align:center;">
                <span style="color:#1a1a2e;font-size:13px;font-weight:700;">Bouwbedrijven</span>
              </td></tr>
              <tr><td style="padding:10px 12px;">
                <p style="margin:0;color:#6b7280;font-size:12px;line-height:1.5;">Aannemers en bouwbedrijven die een extern contactpersoon zoeken.</p>
              </td></tr>
            </table>
          </td>
          <td style="width:33%;padding:0 3px;vertical-align:top;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;overflow:hidden;">
              <tr><td style="background-color:#eef2ff;padding:10px 12px;text-align:center;">
                <span style="color:#1a1a2e;font-size:13px;font-weight:700;">Installatiebedrijven</span>
              </td></tr>
              <tr><td style="padding:10px 12px;">
                <p style="margin:0;color:#6b7280;font-size:12px;line-height:1.5;">Elektra, loodgieterij, HVAC en overige installatiebedrijven.</p>
              </td></tr>
            </table>
          </td>
          <td style="width:33%;padding:0 0 0 6px;vertical-align:top;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:10px;overflow:hidden;">
              <tr><td style="background-color:#eef2ff;padding:10px 12px;text-align:center;">
                <span style="color:#1a1a2e;font-size:13px;font-weight:700;">Productie &amp; Maak</span>
              </td></tr>
              <tr><td style="padding:10px 12px;">
                <p style="margin:0;color:#6b7280;font-size:12px;line-height:1.5;">Metaalbewerking, houtbewerking en kleine fabrieken.</p>
              </td></tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Differentiators -->
  <tr>
    <td style="padding:0 40px 12px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#eef2ff;border-radius:8px;padding:10px 14px;">
            <p style="margin:0;color:#4f46e5;font-size:13px;font-weight:600;">
              &#10024; Geen uitzendbureau, geen tussenpartij &#8212; directe samenwerking tegen normale prijzen.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td style="padding:0 40px 28px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#eef2ff;border-radius:8px;padding:10px 14px;">
            <p style="margin:0;color:#4f46e5;font-size:13px;font-weight:600;">
              &#128273; De IB-aangifte blijft gewoon bij uw huidige accountant.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="padding:0 40px 12px;" align="center">
      <p style="margin:0 0 16px;color:#374151;font-size:15px;line-height:1.7;text-align:left;">
        E&#233;n contactpersoon voor administratie en ICT &#8212; geen fulltime medewerker nodig. Neem vrijblijvend contact op voor een kennismaking.
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
      <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_en_techniek_maart2026"
         style="color:#4f46e5;font-size:14px;text-decoration:none;font-weight:500;">
        Bekijk de volledige propositie op fenofin.nl &#8594;
      </a>
    </td>
  </tr>

  <!-- Section links -->
  <tr>
    <td style="padding:8px 40px 4px;" align="center">
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="padding:0 8px;">
            <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_en_techniek_maart2026#administratie"
               style="color:#6b7280;font-size:12px;text-decoration:none;">Administratie</a>
          </td>
          <td style="color:#d1d5db;">&#183;</td>
          <td style="padding:0 8px;">
            <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_en_techniek_maart2026#vpb"
               style="color:#6b7280;font-size:12px;text-decoration:none;">VPB-aangifte</a>
          </td>
          <td style="color:#d1d5db;">&#183;</td>
          <td style="padding:0 8px;">
            <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_en_techniek_maart2026#ict"
               style="color:#6b7280;font-size:12px;text-decoration:none;">ICT &amp; Netwerk</a>
          </td>
          <td style="color:#d1d5db;">&#183;</td>
          <td style="padding:0 8px;">
            <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_en_techniek_maart2026#doelgroepen"
               style="color:#6b7280;font-size:12px;text-decoration:none;">Doelgroepen</a>
          </td>
          <td style="color:#d1d5db;">&#183;</td>
          <td style="padding:0 8px;">
            <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouw_en_techniek_maart2026#contact"
               style="color:#6b7280;font-size:12px;text-decoration:none;">Contact</a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Signature -->
  <tr>
    <td style="padding:28px 40px 20px;">
      <p style="margin:0 0 4px;color:#374151;font-size:15px;line-height:1.7;">Met vriendelijke groet,</p>
      <p style="margin:12px 0 0;color:#1a1a2e;font-size:15px;font-weight:700;">Folkert Feenstra</p>
      <p style="margin:2px 0 0;color:#6b7280;font-size:13px;">Praktijkopleiding Accountancy | Affiniteit ICT</p>
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
    tpl = ResponseTemplate.objects.filter(slug="bouwbedrijven").first()
    if not tpl:
        return
    tpl.body = BODY.strip()
    tpl.html_template = HTML_TEMPLATE.strip()
    tpl.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0054_update_propositie_links"),
    ]

    operations = [
        migrations.RunPython(update_template, noop),
    ]
