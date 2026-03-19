from django.db import migrations


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FenoFin</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f6fa;font-family:'Segoe UI',Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f6fa;">
<tr><td align="center" style="padding:32px 12px;">

<!-- Main container -->
<table role="presentation" width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);">

  <!-- Header -->
  <tr>
    <td style="padding:28px 40px 20px;border-bottom:1px solid #f0f0f5;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <span style="font-size:22px;font-weight:700;color:#e84e7e;letter-spacing:-0.5px;">FenoFin</span>
          </td>
          <td align="right">
            <span style="font-size:12px;color:#9ca3af;">AI-ge&#239;ntegreerd boekhouden</span>
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
        Mijn naam is Folkert Feenstra, afgestudeerd AA-accountant (MKB) en oprichter van FenoFin.
        Met FenoFin bied ik <strong style="color:#1a1a2e;">AI-ge&#239;ntegreerd boekhouden</strong>
        voor onder andere ZZP en DGA.
      </p>
      <p style="margin:0 0 24px;color:#374151;font-size:15px;line-height:1.75;">
        Mijn waardepropositie voor {bedrijfsnaam} rust op twee pijlers:
        <strong style="color:#1a1a2e;">gestandaardiseerde data-analyse voor advies</strong> en
        <strong style="color:#1a1a2e;">WWFT-compliance</strong>. Door de opzet van ons boekhoudsysteem
        zijn deze analyses uitstekend te automatiseren &#8212; van data-analyse tot visueel
        aantrekkelijke rapportages die u direct met uw klant kunt delen.
      </p>
    </td>
  </tr>

  <!-- Pijler 1: Unieke propositie klant -->
  <tr>
    <td style="padding:0 40px 12px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #f0f0f5;border-radius:12px;overflow:hidden;">
        <!-- Pijler header -->
        <tr>
          <td style="background-color:#fef7f9;padding:16px 24px;border-bottom:1px solid #fce4ec;">
            <p style="margin:0;font-size:11px;font-weight:600;color:#e84e7e;text-transform:uppercase;letter-spacing:1px;">Pijler 1</p>
            <p style="margin:4px 0 0;font-size:17px;font-weight:700;color:#1a1a2e;">Unieke propositie voor uw klant</p>
          </td>
        </tr>
        <!-- Pijler body -->
        <tr>
          <td style="padding:20px 24px;">
            <p style="margin:0 0 10px;color:#6b7280;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Aanleveren &amp; verwerking</p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#e84e7e;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>WhatsApp &amp; Mail</strong> &#8212; uw klant stuurt de inkoopfactuur naar FenoFin
                </td>
              </tr>
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#e84e7e;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>AI herkent</strong> leverancier, leest bedrag en BTW, boekt automatisch in.
                  Banktransacties worden &#8217;s nachts gematcht.
                </td>
              </tr>
            </table>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0 0;">
              <tr>
                <td style="padding:6px 0;">
                  <p style="margin:0 0 4px;color:#6b7280;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">WhatsApp AI Chat &#8212; Cockpit</p>
                  <span style="display:inline-block;background-color:#e84e7e;color:#ffffff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;letter-spacing:0.5px;">UNIEK AAN FENOFIN</span>
                </td>
              </tr>
              <tr>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.6;">
                  &#8212; Verkoopfactuur aanmaken en <strong>direct versturen</strong><br>
                  &#8212; &#8220;Welke facturen staan nog open?&#8221;<br>
                  &#8212; &#8220;Wat is mijn omzet deze maand?&#8221;
                </td>
              </tr>
            </table>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:12px 0 0;">
              <tr>
                <td style="background-color:#f9fafb;border-radius:8px;padding:10px 14px;">
                  <p style="margin:0;color:#6b7280;font-size:13px;font-style:italic;">
                    Geen app openen, geen inloggen &#8212; gewoon appen.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Pijler 2: Unieke propositie administratiekantoor -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:2px solid #e84e7e;border-radius:12px;overflow:hidden;">
        <!-- Pijler header -->
        <tr>
          <td style="background-color:#e84e7e;padding:16px 24px;">
            <p style="margin:0;font-size:11px;font-weight:600;color:rgba(255,255,255,0.8);text-transform:uppercase;letter-spacing:1px;">Pijler 2</p>
            <p style="margin:4px 0 0;font-size:17px;font-weight:700;color:#ffffff;">Unieke propositie voor uw kantoor</p>
          </td>
        </tr>
        <!-- Pijler body -->
        <tr>
          <td style="padding:20px 24px;">
            <p style="margin:0 0 12px;color:#374151;font-size:14px;line-height:1.7;font-weight:500;">
              Hoe wij van waarde kunnen zijn voor uw klanten:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#e84e7e;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">WWFT compliance tools</strong> &#8212;
                  WWFT-analyses op klantniveau als onderdeel van de data-analyse, organisatiestructuur
                  met documentkoppeling waardoor wij compliance-verplichtingen uit handen kunnen nemen
                </td>
              </tr>
              <tr>
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#e84e7e;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">AI data-analyse via RGS</strong> &#8212;
                  door ons RGS-rekeningschema kunnen wij diepgaande analyses maken op klantniveau,
                  aangevuld met AI-gedreven inzichten die wij namens u aan uw klanten kunnen delen
                </td>
              </tr>
            </table>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:14px 0 0;">
              <tr>
                <td style="background-color:#fef7f9;border-radius:8px;padding:10px 14px;">
                  <p style="margin:0;color:#e84e7e;font-size:13px;font-weight:600;">
                    Van boekhouding naar advies &#8212; WWFT-compliance en AI-gedreven inzichten door RGS.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Cashback & samenwerking -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f9fafb;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="padding:20px 24px;">
            <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1a1a2e;">Samenwerking &amp; cashback</p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;vertical-align:top;width:24px;color:#16a34a;font-size:13px;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  Klanten nemen zelf het abonnement &#8212; u verdient mee
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;vertical-align:top;width:24px;color:#16a34a;font-size:13px;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>15% cashback</strong> over het volledige abonnement (inclusief add-ons)
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
    <td style="padding:0 40px 8px;" align="center">
      <p style="margin:0 0 16px;color:#374151;font-size:15px;line-height:1.7;text-align:left;">
        Ik laat het u graag zien. Start met slechts 1 klant als administratiekantoor
        en ontdek wat AI-ge&#239;ntegreerd boekhouden voor uw praktijk kan betekenen.
      </p>
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#e84e7e;border-radius:8px;">
            <a href="https://www.fenofin.nl/propositie/kantoor/?utm_source=email&amp;utm_medium=outreach&amp;utm_campaign=kantoor-mrt2026"
               style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:0.2px;">
              Bekijk de volledige propositie &#8594;
            </a>
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
      <p style="margin:2px 0 0;color:#6b7280;font-size:13px;">AA-accountant (MKB) &middot; Oprichter FenoFin</p>
    </td>
  </tr>

  <!-- Divider -->
  <tr>
    <td style="padding:0 40px;">
      <hr style="border:none;border-top:1px solid #f0f0f5;margin:0;">
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:20px 40px 24px;text-align:center;">
      <p style="margin:0 0 4px;color:#9ca3af;font-size:12px;">
        FenoFin B.V. &middot; <a href="https://www.fenofin.nl" style="color:#e84e7e;text-decoration:none;">fenofin.nl</a>
      </p>
      <p style="margin:0;color:#c4c7cc;font-size:11px;">
        U ontvangt deze e-mail omdat wij denken dat onze diensten relevant zijn voor uw kantoor.
      </p>
    </td>
  </tr>

</table>
<!-- /Main container -->

</td></tr>
</table>
</body>
</html>"""


UPDATED_BODY = """\
{aanhef} {achternaam},

Mijn naam is Folkert Feenstra, afgestudeerd AA-accountant (MKB) en oprichter van FenoFin. Met FenoFin bied ik AI-ge\u00efntegreerd boekhouden voor onder andere ZZP en DGA.

Mijn waardepropositie voor {bedrijfsnaam} rust op twee pijlers: gestandaardiseerde data-analyse voor advies en WWFT-compliance. Door de opzet van ons boekhoudsysteem zijn deze analyses uitstekend te automatiseren \u2014 van data-analyse tot visueel aantrekkelijke rapportages die u direct met uw klant kunt delen.

--- Pijler 1: Unieke propositie voor uw klant ---

Aanleveren & verwerking:
\u2022 WhatsApp & Mail \u2014 uw klant stuurt de inkoopfactuur naar FenoFin
\u2022 AI herkent leverancier, leest bedrag en BTW, boekt automatisch in. Banktransacties worden \u2019s nachts gematcht.

WhatsApp AI Chat \u2014 Cockpit (uniek aan FenoFin):
\u2022 Verkoopfactuur aanmaken en direct versturen
\u2022 \u201cWelke facturen staan nog open?\u201d
\u2022 \u201cWat is mijn omzet deze maand?\u201d

Geen app openen, geen inloggen \u2014 gewoon appen.

--- Pijler 2: Unieke propositie voor uw kantoor ---

Hoe wij van waarde kunnen zijn voor uw klanten:
\u2022 WWFT compliance tools \u2014 WWFT-analyses op klantniveau als onderdeel van de data-analyse, organisatiestructuur met documentkoppeling waardoor wij compliance-verplichtingen uit handen kunnen nemen
\u2022 AI data-analyse via RGS \u2014 door ons RGS-rekeningschema kunnen wij diepgaande analyses maken op klantniveau, aangevuld met AI-gedreven inzichten die wij namens u aan uw klanten kunnen delen

Van boekhouding naar advies \u2014 WWFT-compliance en AI-gedreven inzichten door RGS.

--- Samenwerking & cashback ---

\u2022 Klanten nemen zelf het abonnement \u2014 u verdient mee
\u2022 15% cashback over het volledige abonnement (inclusief add-ons)

Ik laat het u graag zien. Start met slechts 1 klant als administratiekantoor en ontdek wat AI-ge\u00efntegreerd boekhouden voor uw praktijk kan betekenen.

Bekijk de volledige propositie: https://www.fenofin.nl/propositie/kantoor/?utm_source=email&utm_medium=outreach&utm_campaign=kantoor-mrt2026

Met vriendelijke groet,
Folkert Feenstra
AA-accountant (MKB) \u2022 Oprichter FenoFin"""


def update_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    try:
        tpl = ResponseTemplate.objects.get(slug="administratiekantoren")
        tpl.html_template = HTML_TEMPLATE
        tpl.body = UPDATED_BODY
        tpl.save()
    except ResponseTemplate.DoesNotExist:
        pass


def reverse_update(apps, schema_editor):
    """Reverse is handled by migration 0032."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0032_update_kantoor_html_template"),
    ]

    operations = [
        migrations.RunPython(update_template, reverse_update),
    ]
