from django.db import migrations


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FenoFin</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f7;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7;">
<tr><td align="center" style="padding:30px 15px;">

<!-- Main container -->
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">

  <!-- Header bar -->
  <tr>
    <td style="background:linear-gradient(135deg,#e84e7e 0%,#c2185b 100%);padding:32px 40px;text-align:center;">
      <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:700;letter-spacing:-0.5px;">FenoFin</h1>
      <p style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:13px;letter-spacing:0.5px;">Slim. Persoonlijk. Digitaal.</p>
    </td>
  </tr>

  <!-- Body -->
  <tr>
    <td style="padding:36px 40px 20px;">
      <p style="margin:0 0 18px;color:#333333;font-size:15px;line-height:1.7;">
        {aanhef} {achternaam},
      </p>
      <p style="margin:0 0 18px;color:#333333;font-size:15px;line-height:1.7;">
        Mijn naam is Folkert Feenstra, oprichter van FenoFin. Wij helpen administratie&shy;kantoren
        hun dienstverlening te versnellen met slimme AI-tools \u2014 zonder dat u uw werkwijze hoeft
        om te gooien.
      </p>

      <!-- Highlight box -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;">
        <tr>
          <td style="background-color:#fdf2f5;border-left:4px solid #e84e7e;border-radius:0 8px 8px 0;padding:20px 24px;">
            <p style="margin:0 0 6px;font-weight:700;color:#c2185b;font-size:14px;">Wat levert het u op?</p>
            <ul style="margin:0;padding:0 0 0 18px;color:#4a4a4a;font-size:14px;line-height:1.8;">
              <li><strong>WhatsApp AI-assistent</strong> \u2014 beantwoordt klantvragen 24/7 met uw eigen kennisbank</li>
              <li><strong>Automatische WWFT-checks</strong> \u2014 PEP, sanctielijsten &amp; UBO in \xe9\xe9n klik</li>
              <li><strong>RGS-koppeling</strong> \u2014 direct inzicht in de boekhouding van uw klanten</li>
              <li><strong>15% cashback</strong> \u2014 op alle FenoFin-diensten in het eerste jaar</li>
            </ul>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 18px;color:#333333;font-size:15px;line-height:1.7;">
        Ik kom graag langs bij <strong>{bedrijfsnaam}</strong> voor een vrijblijvende demo van
        30 minuten. Geen verplichtingen \u2014 alleen laten zien wat er mogelijk is.
      </p>

      <!-- CTA button -->
      <table role="presentation" cellpadding="0" cellspacing="0" style="margin:28px 0;">
        <tr>
          <td style="background:linear-gradient(135deg,#e84e7e 0%,#c2185b 100%);border-radius:8px;">
            <a href="https://fenofin.nl/contact/" style="display:inline-block;padding:14px 32px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;">
              Gratis demo inplannen &rarr;
            </a>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 8px;color:#333333;font-size:15px;line-height:1.7;">
        Met vriendelijke groet,
      </p>
      <p style="margin:0;color:#333333;font-size:15px;line-height:1.7;font-weight:600;">
        Folkert Feenstra
      </p>
      <p style="margin:2px 0 0;color:#888888;font-size:13px;">
        Oprichter FenoFin &middot; folkert@fenofin.nl &middot; 06-12345678
      </p>
    </td>
  </tr>

  <!-- Divider -->
  <tr>
    <td style="padding:0 40px;">
      <hr style="border:none;border-top:1px solid #eee;margin:0;">
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

Mijn naam is Folkert Feenstra, oprichter van FenoFin. Wij helpen administratiekantoren hun dienstverlening te versnellen met slimme AI-tools \u2014 zonder dat u uw werkwijze hoeft om te gooien.

Wat levert het u op?
\u2022 WhatsApp AI-assistent \u2014 beantwoordt klantvragen 24/7 met uw eigen kennisbank
\u2022 Automatische WWFT-checks \u2014 PEP, sanctielijsten & UBO in \xe9\xe9n klik
\u2022 RGS-koppeling \u2014 direct inzicht in de boekhouding van uw klanten
\u2022 15% cashback \u2014 op alle FenoFin-diensten in het eerste jaar

Ik kom graag langs bij {bedrijfsnaam} voor een vrijblijvende demo van 30 minuten. Geen verplichtingen \u2014 alleen laten zien wat er mogelijk is.

Met vriendelijke groet,
Folkert Feenstra
Oprichter FenoFin"""


UPDATED_SUBJECT = "Samenwerking {bedrijfsnaam} \u00d7 FenoFin \u2014 AI voor administratiekantoren"


def seed_html_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    try:
        tpl = ResponseTemplate.objects.get(slug="administratiekantoren")
        tpl.html_template = HTML_TEMPLATE
        tpl.body = UPDATED_BODY
        tpl.subject = UPDATED_SUBJECT
        tpl.save()
    except ResponseTemplate.DoesNotExist:
        pass


def reverse_seed(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    try:
        tpl = ResponseTemplate.objects.get(slug="administratiekantoren")
        tpl.html_template = ""
        tpl.save()
    except ResponseTemplate.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0030_responsetemplate_html_template"),
    ]

    operations = [
        migrations.RunPython(seed_html_template, reverse_seed),
    ]
