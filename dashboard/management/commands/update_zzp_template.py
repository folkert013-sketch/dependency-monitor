"""One-off command to update klant-zzp-dga template sections."""
from django.core.management.base import BaseCommand
import re


NEW_BODY = """{aanhef} {achternaam},

Mijn naam is Folkert Feenstra, oprichter van FenoFin. FenoFin is een AI-boekhoudsysteem met meekijkservice \u2014 speciaal voor ZZP\u2019ers en DGA\u2019s.

De software verwerkt uw administratie automatisch, een ervaren boekhouder kijkt mee. Veel bedienen via WhatsApp \u2014 geen boekhoudsoftware openen. Zo bespaart u op boekhoudkosten.

\u2713 Zelf boekhouden met AI

U houdt zelf de regie over uw administratie:
\u2022 Facturen insturen \u2014 via WhatsApp of e-mail, de AI leest en boekt automatisch in
\u2022 Banktransacties \u2014 automatisch gematcht aan facturen
\u2022 Overzicht \u2014 altijd inzicht in omzet, kosten en openstaande facturen
Automatiseer de administratie en boekhouding zonder inloggen.

\u2713 Meekijkservice

Komt u er niet uit? Een ervaren boekhouder kijkt mee:
\u2022 Direct overleg \u2014 stel uw vraag wanneer u wilt
\u2022 Checken \u2014 laat uw boekhouding doorlopend checken voor de aangifte
\u2022 Leren \u2014 begrijp wat u boekt en waarom
Bespaar kosten \u2014 meekijkservice om snel te checken of het goed is.

\u2713 Zelf aangifte indienen

Dien zelfstandig uw aangifte in vanuit het systeem:
\u2022 BTW-aangifte \u2014 het systeem berekent, u dient in
\u2022 Of wij doen het \u2014 geen zin of tijd? Wij regelen de aangifte
\u2022 Meekijkservice \u2014 laat uw aangifte controleren voor indiening
Geen tijd? Wij dienen de aangifte voor u in.

Ontdek wat AI-ge\u00efntegreerd boekhouden voor {bedrijfsnaam} kan betekenen \u2014 bespaar op boekhoudkosten.

Bekijk de volledige propositie: https://www.fenofin.nl/propositie/?utm_source=mailing&utm_medium=email&utm_campaign=zzp_propositie_maart2026

Met vriendelijke groet,

Folkert Feenstra
FenoFin B.V. | Zuidlaren
f.feenstra@fenofin.nl | www.fenofin.nl
"""

NEW_SECTIONS = """  <!-- Dienst 1: Zelf boekhouden met AI -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128187;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">Zelf boekhouden met AI</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 8px;color:#374151;font-size:14px;line-height:1.6;">
              U houdt zelf de regie over uw administratie:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Facturen insturen</strong> &#8212; via WhatsApp of e-mail, de AI leest en boekt automatisch in
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Banktransacties</strong> &#8212; automatisch gematcht aan facturen
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Overzicht</strong> &#8212; altijd inzicht in omzet, kosten en openstaande facturen
                </td>
              </tr>
            </table>
            <p style="margin:12px 0 0;color:#6b7280;font-size:13px;font-style:italic;">
              Automatiseer de administratie en boekhouding zonder inloggen.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Dienst 2: Meekijkservice -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128101;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">Meekijkservice</span>
                  <span style="color:#6b7280;font-size:13px;"> &#8212; uniek aan FenoFin</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 8px;color:#374151;font-size:14px;line-height:1.6;">
              Komt u er niet uit? Een ervaren boekhouder kijkt mee:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Direct overleg</strong> &#8212; stel uw vraag wanneer u wilt
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Checken</strong> &#8212; laat uw boekhouding doorlopend checken voor de aangifte
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Leren</strong> &#8212; begrijp wat u boekt en waarom
                </td>
              </tr>
            </table>
            <p style="margin:12px 0 0;color:#6b7280;font-size:13px;font-style:italic;">
              Bespaar kosten &#8212; meekijkservice om snel te checken of het goed is.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- Dienst 3: Zelf aangifte indienen -->
  <tr>
    <td style="padding:0 40px 20px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e7ff;border-radius:12px;overflow:hidden;">
        <tr>
          <td style="background-color:#eef2ff;padding:12px 20px;border-bottom:1px solid #e0e7ff;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="width:28px;vertical-align:middle;">
                  <span style="font-size:18px;">&#128203;</span>
                </td>
                <td>
                  <span style="color:#1a1a2e;font-size:15px;font-weight:700;">Zelf aangifte indienen</span>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 8px;color:#374151;font-size:14px;line-height:1.6;">
              Dien zelfstandig uw aangifte in vanuit het systeem:
            </p>
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>BTW-aangifte</strong> &#8212; het systeem berekent, u dient in
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Of wij doen het</strong> &#8212; geen zin of tijd? Wij regelen de aangifte
                </td>
              </tr>
              <tr>
                <td style="padding:4px 0;color:#4f46e5;font-size:12px;width:20px;vertical-align:top;">&#10003;</td>
                <td style="padding:4px 0;color:#374151;font-size:14px;line-height:1.6;">
                  <strong>Meekijkservice</strong> &#8212; laat uw aangifte controleren voor indiening
                </td>
              </tr>
            </table>
            <p style="margin:12px 0 0;color:#6b7280;font-size:13px;font-style:italic;">
              Geen tijd? Wij dienen de aangifte voor u in.
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  """


class Command(BaseCommand):
    help = "Update klant-zzp-dga template with new sections"

    def handle(self, *args, **options):
        from dashboard.models import ResponseTemplate
        t = ResponseTemplate.objects.get(slug="klant-zzp-dga")

        html = t.html_template
        # Find boundaries
        start = re.search(r'<!-- Dienst 1:', html)
        end = re.search(r'<!-- CTA -->', html)
        if not start or not end:
            self.stderr.write("Could not find section markers")
            return

        html = html[:start.start()] + NEW_SECTIONS + html[end.start():]

        t.body = NEW_BODY.strip()
        t.html_template = html
        t.save()
        self.stdout.write(self.style.SUCCESS("Template updated"))
