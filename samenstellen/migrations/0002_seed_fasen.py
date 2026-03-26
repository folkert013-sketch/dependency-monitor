"""Seed de 6 fasen van de samenstelopdracht conform NV COS 4410."""

from django.db import migrations


FASEN = [
    {
        "fase_key": "randvoorwaarden",
        "naam": "Randvoorwaarden",
        "order": 0,
        "run_nummer": 1,
        "beschrijving": (
            "Ethische voorschriften en kwaliteitsbeheersing die van toepassing zijn "
            "op de samenstelopdracht. De accountant moet voldoen aan de fundamentele "
            "beginselen en kwaliteitsnormen."
        ),
        "doelen": (
            "- Beoordeel naleving van de fundamentele beginselen: integriteit, "
            "objectiviteit, vakbekwaamheid en zorgvuldigheid, geheimhouding, "
            "professioneel gedrag\n"
            "- Controleer onafhankelijkheid en naleving van de ViO\n"
            "- Beoordeel het stelsel van kwaliteitsbeheersing van het kantoor\n"
            "- Controleer naleving van de NVKS (Nadere Voorschriften Kwaliteitssystemen)"
        ),
        "randvoorwaarden": (
            "- Het accountantskantoor beschikt over een stelsel van kwaliteitsbeheersing\n"
            "- De accountant voldoet aan de VGBA (Verordening Gedrags- en Beroepsregels Accountants)\n"
            "- De accountant voldoet aan de ViO (Verordening inzake de Onafhankelijkheid)\n"
            "- Naleving van de NVKS is geborgd"
        ),
        "referenties": (
            "VGBA, ViO, NVKS, Standaard 4410 paragraaf 1-22"
        ),
    },
    {
        "fase_key": "aanvaarding",
        "naam": "Aanvaarding en continuering",
        "order": 1,
        "run_nummer": 1,
        "beschrijving": (
            "Beoordeel of de klant en opdracht kunnen worden aanvaard of gecontinueerd. "
            "Stel de opdrachtvoorwaarden vast en stem deze af met de klant."
        ),
        "doelen": (
            "- Beoordeel de integriteit van de klant en het risico op witwassen "
            "(Wwft)\n"
            "- Breng de organisatiestructuur van het bedrijf in kaart\n"
            "- Voer identificatie en verificatie van de klant uit (Wwft)\n"
            "- Beoordeel vakbekwaamheid: beschikbare deskundigheid, tijd en "
            "medewerkers\n"
            "- Stel opdrachtvoorwaarden vast: doel, verantwoordelijkheden, "
            "verwachtingen\n"
            "- Maak een risico-inschatting voor witwassen en terrorismefinanciering\n"
            "- Beoordeel overige overwegingen: capaciteit, vergoeding, "
            "kredietwaardigheid, continuiteit"
        ),
        "randvoorwaarden": (
            "- Integriteitsonderzoek klant is uitgevoerd (collegiaal overleg, "
            "reputatie, branche, houding management)\n"
            "- Identificatie en verificatie conform Wwft is voltooid\n"
            "- Opdrachtvoorwaarden zijn schriftelijk vastgelegd in een "
            "opdrachtbevestiging\n"
            "- Het management erkent zijn verantwoordelijkheid bij de "
            "samenstelopdracht\n"
            "- Er zijn geen aanwijzingen dat de klant niet zal meewerken\n"
            "- Voldoende deskundigheid en capaciteit beschikbaar"
        ),
        "referenties": (
            "Standaard 4410 paragraaf 23-26, NVKS artikel 5/10/11/27, "
            "VGBA artikel 14 en 21 lid 3, Wwft artikel 33, "
            "NBA-handreiking 1124"
        ),
    },
    {
        "fase_key": "inzicht",
        "naam": "Inzicht",
        "order": 2,
        "run_nummer": 1,
        "beschrijving": (
            "Verkrijg inzicht in de huishouding van de klant, diens activiteiten "
            "en het stelsel van financiele verslaggeving."
        ),
        "doelen": (
            "- Verwerf inzicht in de bedrijfsactiviteiten en de branche\n"
            "- Breng de organisatiestructuur en het management in kaart\n"
            "- Begrijp het toegepaste stelsel van financiele verslaggeving "
            "(RJ, IFRS, fiscale grondslagen)\n"
            "- Identificeer relevante wet- en regelgeving\n"
            "- Beoordeel de administratieve organisatie en interne beheersing\n"
            "- Analyseer de financiele gegevens uit de concept jaarrekening"
        ),
        "randvoorwaarden": (
            "- De concept jaarrekening is beschikbaar voor analyse\n"
            "- Het stelsel van financiele verslaggeving is geidentificeerd\n"
            "- Er is voldoende inzicht in de bedrijfsactiviteiten om de "
            "jaarrekening te kunnen samenstellen"
        ),
        "referenties": (
            "Standaard 4410 paragraaf 27-29"
        ),
    },
    {
        "fase_key": "samenstellen",
        "naam": "Samenstellen",
        "order": 3,
        "run_nummer": 1,
        "beschrijving": (
            "Stel de jaarrekening samen op basis van de verkregen gegevens. "
            "Bespreek significante aangelegenheden en stel correcties voor."
        ),
        "doelen": (
            "- Stel de jaarrekening samen op basis van het verkregen inzicht\n"
            "- Identificeer significante aangelegenheden en oordeelsvorming\n"
            "- Beoordeel de plausibiliteit van de financiele gegevens\n"
            "- Stel correctievoorstellen op waar nodig\n"
            "- Bespreek bevindingen en bespreekpunten\n"
            "- Documenteer de uitgevoerde werkzaamheden"
        ),
        "randvoorwaarden": (
            "- Het inzicht in de entiteit is voldoende voor het samenstellen\n"
            "- De accountant heeft alle benodigde informatie ontvangen\n"
            "- Significante zaken worden besproken en gedocumenteerd\n"
            "- Correcties worden voorgesteld aan het management"
        ),
        "referenties": (
            "Standaard 4410 paragraaf 30-38"
        ),
    },
    {
        "fase_key": "nalezen",
        "naam": "Nalezen",
        "order": 4,
        "run_nummer": 2,
        "beschrijving": (
            "Lees de definitieve jaarrekening na en controleer of alle "
            "correcties zijn verwerkt."
        ),
        "doelen": (
            "- Controleer of alle correctievoorstellen uit run 1 zijn verwerkt\n"
            "- Beoordeel de volledigheid van de definitieve jaarrekening\n"
            "- Controleer de plausibiliteit van de eindcijfers\n"
            "- Verifieer de consistentie van de grondslagen\n"
            "- Controleer de volledigheid van de toelichtingen"
        ),
        "randvoorwaarden": (
            "- De definitieve jaarrekening is geupload\n"
            "- Alle correctievoorstellen uit run 1 zijn beoordeeld door het management\n"
            "- De jaarrekening is compleet en voldoet aan het gekozen stelsel"
        ),
        "referenties": (
            "Standaard 4410 paragraaf 39"
        ),
    },
    {
        "fase_key": "verklaring",
        "naam": "Samenstellingsverklaring",
        "order": 5,
        "run_nummer": 2,
        "beschrijving": (
            "Stel de samenstellingsverklaring op en documenteer het dossier."
        ),
        "doelen": (
            "- Stel de samenstellingsverklaring op conform NV COS 4410\n"
            "- Documenteer het samenstelopdrachtdossier\n"
            "- Vermeld het toegepaste stelsel van financiele verslaggeving\n"
            "- Verwijs naar de verantwoordelijkheid van het management\n"
            "- Onderteken en dateer de verklaring"
        ),
        "randvoorwaarden": (
            "- Alle eerdere fasen zijn succesvol afgerond\n"
            "- De definitieve jaarrekening is goedgekeurd door het management\n"
            "- Het dossier is volledig gedocumenteerd\n"
            "- De verklaring voldoet aan alle vormvereisten van NV COS 4410"
        ),
        "referenties": (
            "Standaard 4410 paragraaf 40-43"
        ),
    },
]


def seed_fasen(apps, schema_editor):
    Fase = apps.get_model("samenstellen", "Fase")
    for data in FASEN:
        Fase.objects.update_or_create(
            fase_key=data["fase_key"],
            defaults=data,
        )


def reverse_seed(apps, schema_editor):
    Fase = apps.get_model("samenstellen", "Fase")
    Fase.objects.filter(
        fase_key__in=[f["fase_key"] for f in FASEN]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("samenstellen", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_fasen, reverse_seed),
    ]
