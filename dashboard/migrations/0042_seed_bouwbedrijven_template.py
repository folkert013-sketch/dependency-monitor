from django.db import migrations


BOUW_BODY = """\
{aanhef} {achternaam},

Mijn naam is Folkert Feenstra, ZZP'er met expertise in financiële administratie en ICT.

Ik werk direct samen met bouwbedrijven zoals {bedrijfsnaam} en bied drie diensten aan:

• Financiële administratie en automatisering — administratie bijhouden en processen automatiseren
• Aangifte VPB — indienen of als concept voorbereiden voor uw accountant
• ICT en netwerkbeheer — internet, netwerken en wifi opzetten en beheren

Geen uitzendbureau, geen tussenpartij — directe samenwerking tegen normale prijzen.
De IB-aangifte blijft gewoon bij uw huidige accountant.

Interesse in een vrijblijvend gesprek? Stuur mij een mail of bel gerust:
f.feenstra@fenofin.nl | 06-12622344

Meer lezen? Bekijk de volledige propositie op fenofin.nl/propositie/bouw-en-techniek/

Met vriendelijke groet,

Folkert Feenstra
FenoFin B.V. | Zuidlaren
f.feenstra@fenofin.nl | www.fenofin.nl
"""


BOUW_HTML = """\
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
        Mijn naam is Folkert Feenstra, ZZP&#8217;er met expertise in
        <strong style="color:#1a1a2e;">financi&#235;le administratie</strong> en
        <strong style="color:#1a1a2e;">ICT</strong>.
        Ik werk direct samen met bouwbedrijven zoals {bedrijfsnaam}.
      </p>
      <p style="margin:0 0 8px;color:#374151;font-size:15px;line-height:1.75;">
        Drie diensten die uw bedrijf direct ondersteunen:
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
                  <strong style="color:#1a1a2e;">Financi&#235;le administratie en automatisering</strong> &#8212;
                  administratie bijhouden en processen automatiseren
                </td>
              </tr>
              <tr>
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">Aangifte VPB</strong> &#8212;
                  indienen of als concept voorbereiden voor uw accountant
                </td>
              </tr>
              <tr>
                <td style="padding:8px 0;vertical-align:top;width:24px;color:#4f46e5;font-size:13px;">&#10003;</td>
                <td style="padding:8px 0;color:#374151;font-size:14px;line-height:1.65;">
                  <strong style="color:#1a1a2e;">ICT en netwerkbeheer</strong> &#8212;
                  internet, netwerken en wifi opzetten en beheren
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Info blokken -->
  <tr>
    <td style="padding:0 40px 12px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#eef2ff;border-radius:8px;padding:10px 14px;">
            <p style="margin:0;color:#4f46e5;font-size:13px;font-weight:600;">
              Geen uitzendbureau &#8212; directe samenwerking tegen normale prijzen.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td style="padding:0 40px 24px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#eef2ff;border-radius:8px;padding:10px 14px;">
            <p style="margin:0;color:#4f46e5;font-size:13px;font-weight:600;">
              De IB-aangifte blijft gewoon bij uw huidige accountant.
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
        Interesse in een vrijblijvend gesprek? Ik hoor graag van u.
      </p>
      <table role="presentation" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background-color:#4f46e5;border-radius:8px;">
            <a href="mailto:f.feenstra@fenofin.nl?subject=Contact%20FenoFin%20%E2%80%94%20{bedrijfsnaam}"
               style="display:inline-block;padding:14px 36px;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;letter-spacing:0.2px;">
              Neem direct contact op &#8594;
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Propositie link -->
  <tr>
    <td style="padding:12px 40px 8px;" align="center">
      <a href="https://www.fenofin.nl/propositie/bouw-en-techniek/?utm_source=mailing&amp;utm_medium=email&amp;utm_campaign=bouwbedrijven_maart2026"
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


def seed_bouwbedrijven_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    # Try to reuse category from existing kantoor template
    category = None
    try:
        existing = ResponseTemplate.objects.get(slug="administratiekantoren")
        category = existing.category
    except ResponseTemplate.DoesNotExist:
        pass

    ResponseTemplate.objects.update_or_create(
        slug="bouwbedrijven",
        defaults={
            "name": "Bouwbedrijven \u2014 ICT & Financieel",
            "subject": "FenoFin \u2014 Financi\u00eble administratie, VPB-aangifte en ICT voor {bedrijfsnaam}",
            "body": BOUW_BODY,
            "html_template": BOUW_HTML,
            "is_starred": False,
            "category": category,
            "order": 0,
        },
    )


def remove_bouwbedrijven_template(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    ResponseTemplate.objects.filter(slug="bouwbedrijven").delete()


def update_klant_propositie_url(apps, schema_editor):
    """Update klant template URL from /propositie/klant/ to /propositie/"""
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    try:
        tpl = ResponseTemplate.objects.get(slug="klant-zzp-dga")
        tpl.body = tpl.body.replace("/propositie/klant/", "/propositie/")
        tpl.html_template = tpl.html_template.replace("/propositie/klant/", "/propositie/")
        tpl.save()
    except ResponseTemplate.DoesNotExist:
        pass


def revert_klant_propositie_url(apps, schema_editor):
    """Revert klant template URL from /propositie/ back to /propositie/klant/"""
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    try:
        tpl = ResponseTemplate.objects.get(slug="klant-zzp-dga")
        # Only replace the exact propositie/ that isn't followed by kantoor/ or bouw-en-techniek/
        tpl.body = tpl.body.replace(
            "/propositie/?utm_source=", "/propositie/klant/?utm_source="
        )
        tpl.html_template = tpl.html_template.replace(
            "/propositie/?utm_source=", "/propositie/klant/?utm_source="
        )
        tpl.save()
    except ResponseTemplate.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0041_add_assigned_template_to_prospect"),
    ]

    operations = [
        migrations.RunPython(seed_bouwbedrijven_template, remove_bouwbedrijven_template),
        migrations.RunPython(update_klant_propositie_url, revert_klant_propositie_url),
    ]
