from django.db import migrations


DEMO_BODY = """\
{aanhef} {achternaam},

Mijn naam is Folkert Feenstra, oprichter van FenoFin — Agentic Accounting voor ZZP en DGA.

Graag kom ik vrijblijvend bij {bedrijfsnaam} langs om een persoonlijke demo te geven. In 20 minuten laat ik u zien hoe onze twee kernpijlers uw kantoor direct versterken:

• AI data-analyse via RGS — gestandaardiseerde analyses op klantniveau die u als adviesrapportage met uw klant kunt delen.
• WWFT compliance — standaard inbegrepen in elke administratie, compliance-verplichtingen geautomatiseerd.

Beide analyses komen voort uit ons RGS-rekeningschema en ontwikkelen zich continu.

Wilt u het zelf zien? Stuur mij een mail en ik plan graag een moment in:
f.feenstra@fenofin.nl

Meer lezen? Bekijk de volledige propositie op fenofin.nl/propositie/kantoor/

Met vriendelijke groet,

Folkert Feenstra
FenoFin B.V. | Zuidlaren
f.feenstra@fenofin.nl | www.fenofin.nl
"""


DEMO_HTML = """\
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
            <span style="font-size:12px;color:#9ca3af;">Agentic Accounting</span>
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
        Mijn naam is Folkert Feenstra, oprichter van FenoFin &#8212;
        <strong style="color:#1a1a2e;">Agentic Accounting</strong> voor ZZP en DGA.
        Graag kom ik vrijblijvend bij {bedrijfsnaam} langs om een
        <strong style="color:#1a1a2e;">persoonlijke demo van 20 minuten</strong> te geven.
      </p>
      <p style="margin:0 0 8px;color:#374151;font-size:15px;line-height:1.75;">
        Twee analyses die uw kantoor direct versterken:
      </p>
    </td>
  </tr>

  <!-- Kernpropositie blok -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="padding:20px 24px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">AI data-analyse via RGS</strong> &#8212;
                  gestandaardiseerde analyses op klantniveau dankzij ons RGS-rekeningschema,
                  aangevuld met AI-gedreven inzichten die u als adviesrapportage met uw klant kunt delen
                </td>
              </tr>
              <tr>
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">WWFT compliance</strong> &#8212;
                  standaard inbegrepen in elke administratie; compliance-verplichtingen
                  geautomatiseerd inclusief organisatiestructuur en documentkoppeling
                </td>
              </tr>
            </table>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:14px 0 0;">
              <tr>
                <td style="background-color:#eef2ff;border-radius:8px;padding:10px 14px;">
                  <p style="margin:0;color:#4f46e5;font-size:13px;font-weight:600;">
                    Beide analyses komen voort uit ons RGS-rekeningschema en ontwikkelen zich continu.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Demo CTA -->
  <tr>
    <td style="padding:0 40px 12px;" align="center">
      <p style="margin:0 0 16px;color:#374151;font-size:15px;line-height:1.7;text-align:left;">
        Ik kom graag bij u langs om te laten zien hoe dit er in de praktijk uitziet &#8212;
        geheel vrijblijvend en afgestemd op uw kantoor.
      </p>
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#4f46e5;border-radius:8px;">
            <a href="mailto:f.feenstra@fenofin.nl?subject=Demo%20aanvraag%20FenoFin"
               style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:0.2px;">
              Vraag een gratis demo aan &#8594;
            </a>
          </td>
        </tr>
      </table>
      <p style="margin:8px 0 0;color:#9ca3af;font-size:12px;">via Teams of op kantoor</p>
    </td>
  </tr>

  <!-- Propositie link -->
  <tr>
    <td style="padding:12px 40px 8px;" align="center">
      <a href="https://www.fenofin.nl/propositie/kantoor/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=kantoren_demo_maart2026"
         style="color:#4f46e5;font-size:14px;text-decoration:none;font-weight:500;">
        Bekijk de volledige propositie &#8594;
      </a>
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


def seed_kantoor_demo_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    TemplateCategory = apps.get_model("dashboard", "TemplateCategory")

    # Use the same category as the existing kantoor template if available
    category = None
    try:
        existing = ResponseTemplate.objects.get(slug="administratiekantoren")
        category = existing.category
    except ResponseTemplate.DoesNotExist:
        pass

    ResponseTemplate.objects.update_or_create(
        slug="administratiekantoren-demo",
        defaults={
            "name": "Administratiekantoren \u2014 Demo",
            "subject": "FenoFin \u2014 AI data-analyse en WWFT-compliance voor uw kantoor",
            "body": DEMO_BODY,
            "html_template": DEMO_HTML,
            "is_starred": False,
            "category": category,
            "order": 0,
        },
    )


def remove_kantoor_demo_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    ResponseTemplate.objects.filter(slug="administratiekantoren-demo").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0038_update_kantoor_template_v3"),
    ]

    operations = [
        migrations.RunPython(seed_kantoor_demo_template, remove_kantoor_demo_template),
    ]
