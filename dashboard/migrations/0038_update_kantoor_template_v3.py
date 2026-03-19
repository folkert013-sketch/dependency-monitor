from django.db import migrations


KANTOOR_HTML = """\
<!DOCTYPE html>
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
      <p style="margin:0 0 16px;color:#374151;font-size:15px;line-height:1.75;">
        Mijn waardepropositie voor {bedrijfsnaam} rust op twee pijlers:
        <strong style="color:#1a1a2e;">gestandaardiseerde data-analyse voor advies</strong> en
        <strong style="color:#1a1a2e;">WWFT-compliance</strong>. Door de opzet van ons boekhoudsysteem
        zijn deze analyses uitstekend te automatiseren &#8212; van data-analyse tot visueel
        aantrekkelijke rapportages die u direct met uw klant kunt delen.
      </p>

      <!-- Opsomming na waardepropositie -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <tr>
          <td style="padding:6px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
          <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.6;">
            <strong style="color:#1a1a2e;">Vanaf 1 klant</strong> &#8212; u kunt direct starten, zonder minimale afname
          </td>
        </tr>
        <tr>
          <td style="padding:6px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
          <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.6;">
            <strong style="color:#1a1a2e;">Vrijblijvende demo</strong> &#8212; ik laat u graag persoonlijk zien wat FenoFin kan betekenen
          </td>
        </tr>
        <tr>
          <td style="padding:6px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
          <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.6;">
            <strong style="color:#1a1a2e;">Graag in contact</strong> &#8212; ik licht onze waardepropositie graag toe in een kort gesprek
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Pijler 1: Unieke propositie klant -->
  <tr>
    <td style="padding:0 40px 12px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <!-- Pijler header -->
        <tr>
          <td style="background-color:#eef2ff;padding:16px 24px;border-bottom:1px solid #e0e7ff;">
            <p style="margin:0;font-size:11px;font-weight:600;color:#4f46e5;text-transform:uppercase;letter-spacing:1px;">Pijler 1</p>
            <p style="margin:4px 0 0;font-size:17px;font-weight:700;color:#1a1a2e;">Unieke propositie voor uw klant</p>
          </td>
        </tr>
        <!-- Pijler body -->
        <tr>
          <td style="padding:20px 24px;">
            <p style="margin:0 0 10px;color:#6b7280;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Aanleveren &amp; verwerking</p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>WhatsApp &amp; Mail</strong> &#8212; uw klant stuurt de inkoopfactuur naar FenoFin
                </td>
              </tr>
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
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
                  <span style="display:inline-block;background-color:#4f46e5;color:#ffffff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;letter-spacing:0.5px;">UNIEK AAN FENOFIN</span>
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
                <td style="background-color:#f8fafc;border-radius:8px;padding:10px 14px;">
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
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:2px solid #4f46e5;border-radius:12px;overflow:hidden;">
        <!-- Pijler header -->
        <tr>
          <td style="background-color:#4f46e5;padding:16px 24px;">
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
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">WWFT compliance tools</strong> &#8212;
                  WWFT-analyses op klantniveau als onderdeel van de data-analyse, organisatiestructuur
                  met documentkoppeling waardoor wij compliance-verplichtingen uit handen kunnen nemen
                </td>
              </tr>
              <tr>
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">AI data-analyse via RGS</strong> &#8212;
                  door ons RGS-rekeningschema kunnen wij diepgaande analyses maken op klantniveau,
                  aangevuld met AI-gedreven inzichten die u met uw klanten kunt delen
                </td>
              </tr>
            </table>

            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:14px 0 0;">
              <tr>
                <td style="background-color:#eef2ff;border-radius:8px;padding:10px 14px;">
                  <p style="margin:0;color:#4f46e5;font-size:13px;font-weight:600;">
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

  <!-- Bezwaren-sectie -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#fdf2f8;border:1px solid #fce7f3;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="padding:20px 24px 12px;">
            <p style="margin:0 0 4px;color:#6b7280;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Veelgestelde vraag</p>
            <p style="margin:0;font-size:15px;font-weight:700;color:#1a1a2e;line-height:1.6;font-style:italic;">
              &#8220;Wij zijn net gewend aan ons huidige pakket &#8212; weer een nieuw boekhoudsysteem?&#8221;
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:4px 24px 20px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#9ca3af;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.65;">
                  FenoFin is het boekhoudsysteem voor <strong style="color:#1a1a2e;">uw klant</strong> &#8212; niet ter vervanging van &#250;w kantoorpakket
                </td>
              </tr>
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#9ca3af;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">Data-analyse zit standaard in elke administratie</strong> &#8212; daaruit volgt zowel advies als WWFT-compliance
                </td>
              </tr>
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#9ca3af;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.65;">
                  U ontvangt rapportages en bepaalt zelf: <strong style="color:#1a1a2e;">actie ondernemen, vastleggen in uw dossier, of delen met de klant</strong>
                </td>
              </tr>
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#9ca3af;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.65;">
                  In tegenstelling tot andere boekhoudpakketten biedt FenoFin deze analyses ge&#239;ntegreerd &#8212; en ze <strong style="color:#1a1a2e;">ontwikkelen zich continu</strong>
                </td>
              </tr>
              <tr>
                <td style="padding:6px 0;vertical-align:top;width:24px;color:#9ca3af;font-size:13px;">&#10003;</td>
                <td style="padding:6px 0;color:#374151;font-size:14px;line-height:1.65;">
                  Uw klant neemt zelf een abonnement &#8594; u ontvangt <strong style="color:#1a1a2e;">cashback</strong> en verbetert tegelijk uw dienstverlening
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
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8fafc;border-radius:12px;overflow:hidden;">
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
          <td style="background-color:#4f46e5;border-radius:8px;">
            <a href="https://www.fenofin.nl/propositie/kantoor/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=kantoren_maart2026_mailing"
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


def update_kantoor_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    try:
        tpl = ResponseTemplate.objects.get(slug="administratiekantoren")
        tpl.html_template = KANTOOR_HTML
        tpl.save()
    except ResponseTemplate.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0037_add_tracking_event"),
    ]

    operations = [
        migrations.RunPython(update_kantoor_template, migrations.RunPython.noop),
    ]
