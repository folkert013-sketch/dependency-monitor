from django.db import migrations


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FenoFin</title>
</head>
<body style="margin:0;padding:0;background-color:#f9fafb;font-family:'Segoe UI',Arial,Helvetica,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f9fafb;">
<tr><td align="center" style="padding:40px 15px;">

<!-- Main container -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.05);">

  <!-- Header -->
  <tr>
    <td style="padding:32px 40px 24px;text-align:left;border-bottom:2px solid #fce4ec;">
      <h1 style="margin:0;color:#e84e7e;font-size:24px;font-weight:700;letter-spacing:-0.5px;">FenoFin</h1>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="padding:32px 40px 20px;">
      <p style="margin:0 0 18px;color:#1a1a2e;font-size:15px;line-height:1.7;">
        {aanhef} {achternaam},
      </p>
      <p style="margin:0 0 18px;color:#333333;font-size:15px;line-height:1.7;">
        Mijn naam is Folkert Feenstra, oprichter van FenoFin. Wij bouwen aan
        verdergaande automatisering en AI voor administratie&shy;kantoren \u2014 zodat u
        meer tijd overhoudt voor advies en persoonlijk contact met uw klanten.
      </p>

      <p style="margin:0 0 12px;font-weight:700;color:#1a1a2e;font-size:15px;">
        Wat bieden wij {bedrijfsnaam}?
      </p>

      <!-- USP blocks -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <!-- USP 1 -->
        <tr>
          <td style="padding:14px 18px;background-color:#fef7f9;border-radius:8px;">
            <p style="margin:0 0 4px;font-weight:700;color:#e84e7e;font-size:14px;">&#x1F4AC; WhatsApp AI Chat</p>
            <p style="margin:0;color:#4a4a4a;font-size:14px;line-height:1.6;">
              Uw klanten appen facturen, stellen vragen en maken verkoopfacturen via WhatsApp.
              Met tool calling: \u201cWelke facturen staan open?\u201d, \u201cWat is mijn omzet?\u201d
            </p>
          </td>
        </tr>
        <tr><td style="height:8px;"></td></tr>
        <!-- USP 2 -->
        <tr>
          <td style="padding:14px 18px;background-color:#f0f7ff;border-radius:8px;">
            <p style="margin:0 0 4px;font-weight:700;color:#2563eb;font-size:14px;">\u2699\ufe0f Automatische verwerking</p>
            <p style="margin:0;color:#4a4a4a;font-size:14px;line-height:1.6;">
              AI herkent de leverancier, leest bedrag en BTW, en boekt automatisch in.
              Banktransacties worden \u2019s nachts gematcht.
            </p>
          </td>
        </tr>
        <tr><td style="height:8px;"></td></tr>
        <!-- USP 3 -->
        <tr>
          <td style="padding:14px 18px;background-color:#f0fdf4;border-radius:8px;">
            <p style="margin:0 0 4px;font-weight:700;color:#16a34a;font-size:14px;">\u2705 WWFT compliance</p>
            <p style="margin:0;color:#4a4a4a;font-size:14px;line-height:1.6;">
              PEP, sanctielijsten &amp; UBO checks als vast onderdeel van de data-analyse.
              Altijd up-to-date, zonder extra werk.
            </p>
          </td>
        </tr>
        <tr><td style="height:8px;"></td></tr>
        <!-- USP 4 -->
        <tr>
          <td style="padding:14px 18px;background-color:#fdf4ff;border-radius:8px;">
            <p style="margin:0 0 4px;font-weight:700;color:#9333ea;font-size:14px;">&#x1F4CA; AI data-analyse via RGS</p>
            <p style="margin:0;color:#4a4a4a;font-size:14px;line-height:1.6;">
              Diepgaande analyses en visuele rapportages op basis van RGS \u2014
              namens uw kantoor, richting uw klanten.
            </p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 18px;color:#333333;font-size:15px;line-height:1.7;">
        Ik laat het u graag zien in een vrijblijvende demo. We starten bewust met een
        beperkt aantal kantoren, zodat we de kwaliteit kunnen waarborgen.
      </p>

      <!-- CTA button -->
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:24px 0;">
        <tr>
          <td style="background-color:#e84e7e;border-radius:8px;">
            <a href="https://www.fenofin.nl/propositie/kantoor/?utm_source=facebook&utm_medium=paid&utm_campaign=fb-accountants-mrt2026" style="display:inline-block;padding:14px 32px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;">
              Bekijk de propositie &rarr;
            </a>
          </td>
        </tr>
      </table>

      <!-- Cashback mention -->
      <p style="margin:0 0 24px;color:#666666;font-size:13px;line-height:1.6;background-color:#fef7f9;padding:12px 16px;border-radius:6px;">
        &#x1F381; <strong>Early adopter voordeel:</strong> kantoren die nu instappen ontvangen
        <strong>15% cashback</strong> op alle FenoFin-diensten in het eerste jaar.
      </p>

      <p style="margin:0 0 8px;color:#333333;font-size:15px;line-height:1.7;">
        Met vriendelijke groet,
      </p>
      <p style="margin:0;color:#1a1a2e;font-size:15px;line-height:1.7;font-weight:600;">
        Folkert Feenstra
      </p>
      <p style="margin:2px 0 0;color:#888888;font-size:13px;">
        Oprichter FenoFin
      </p>
    </td>
  </tr>

  <!-- Divider -->
  <tr>
    <td style="padding:0 40px;">
      <hr style="border:none;border-top:1px solid #f0f0f0;margin:0;">
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:20px 40px 28px;text-align:center;">
      <p style="margin:0 0 6px;color:#aaaaaa;font-size:12px;">
        FenoFin B.V. &middot; fenofin.nl
      </p>
      <p style="margin:0;color:#cccccc;font-size:11px;">
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

Mijn naam is Folkert Feenstra, oprichter van FenoFin. Wij bouwen aan verdergaande automatisering en AI voor administratiekantoren \u2014 zodat u meer tijd overhoudt voor advies en persoonlijk contact met uw klanten.

Wat bieden wij {bedrijfsnaam}?

\u2022 WhatsApp AI Chat \u2014 uw klanten appen facturen, stellen vragen en maken verkoopfacturen via WhatsApp. Met tool calling: "Welke facturen staan open?", "Wat is mijn omzet?"
\u2022 Automatische verwerking \u2014 AI herkent de leverancier, leest bedrag en BTW, en boekt automatisch in. Banktransacties worden \u2019s nachts gematcht.
\u2022 WWFT compliance \u2014 PEP, sanctielijsten & UBO checks als vast onderdeel van de data-analyse.
\u2022 AI data-analyse via RGS \u2014 diepgaande analyses en visuele rapportages namens uw kantoor.

Ik laat het u graag zien in een vrijblijvende demo. We starten bewust met een beperkt aantal kantoren, zodat we de kwaliteit kunnen waarborgen.

Bekijk de propositie: https://www.fenofin.nl/propositie/kantoor/?utm_source=facebook&utm_medium=paid&utm_campaign=fb-accountants-mrt2026

Early adopter voordeel: kantoren die nu instappen ontvangen 15% cashback op alle FenoFin-diensten in het eerste jaar.

Met vriendelijke groet,
Folkert Feenstra
Oprichter FenoFin"""


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
    """Reverse is handled by migration 0031 which has the previous version."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0031_seed_kantoor_html_template"),
    ]

    operations = [
        migrations.RunPython(update_template, reverse_update),
    ]
