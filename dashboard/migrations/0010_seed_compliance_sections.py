"""
Data migration: seed the 10 WWFT compliance sections with base content.
"""

from django.db import migrations


SECTIONS = [
    {
        "key": "wettelijke_basis",
        "title": "Wettelijke basis",
        "order": 0,
        "office_action_required": False,
        "body": (
            "De Wet ter voorkoming van witwassen en financieren van terrorisme (Wwft) verplicht "
            "instellingen om cliëntenonderzoek te verrichten en ongebruikelijke transacties te melden. "
            "De wet is van toepassing op onder meer accountants, belastingadviseurs, advocaten en "
            "notarissen.\n\n"
            "Relevante wetgeving:\n"
            "- Wwft (Wet ter voorkoming van witwassen en financieren van terrorisme)\n"
            "- Uitvoeringsbesluit Wwft 2018\n"
            "- Uitvoeringsregeling Wwft 2018\n"
            "- Sanctiewet 1977 en Sanctieregeling terrorisme\n"
            "- EU Anti-Money Laundering Directives (AMLD 4, 5, 6)\n"
            "- Wet toezicht trustkantoren 2018 (Wtt 2018)"
        ),
    },
    {
        "key": "clientenonderzoek",
        "title": "Cliëntenonderzoek",
        "order": 1,
        "office_action_required": True,
        "office_action_description": (
            "Het kantoor moet voor elke nieuwe cliënt een cliëntenonderzoek uitvoeren voordat "
            "de dienstverlening start. Documenteer de identiteit, de UBO's en het doel van de relatie. "
            "Bewaar kopieën van identiteitsdocumenten en leg de verificatie vast in het dossier."
        ),
        "body": (
            "Het cliëntenonderzoek (CDD - Customer Due Diligence) is de kern van de Wwft-verplichtingen. "
            "Bij het aangaan van een zakelijke relatie moet het kantoor:\n\n"
            "1. De identiteit van de cliënt vaststellen en verifiëren (art. 3 Wwft)\n"
            "2. De identiteit van de uiteindelijk belanghebbende (UBO) vaststellen (art. 3 lid 1 sub b)\n"
            "3. Het doel en de beoogde aard van de zakelijke relatie vaststellen (art. 3 lid 1 sub d)\n"
            "4. Een voortdurende controle uitoefenen op de zakelijke relatie (art. 3 lid 1 sub e)\n\n"
            "Het UBO-register (Handelsregister KvK) kan worden geraadpleegd voor UBO-verificatie."
        ),
    },
    {
        "key": "risicobeleid",
        "title": "Risicobeleid kantoorniveau",
        "order": 2,
        "office_action_required": True,
        "office_action_description": (
            "Het kantoor moet een schriftelijk risicobeleid opstellen dat minimaal jaarlijks wordt "
            "geëvalueerd. Dit beleid moet risicofactoren benoemen voor cliënten, diensten, "
            "transacties en geografische gebieden."
        ),
        "body": (
            "Elke Wwft-instelling moet een risicobeoordeling op kantoor-/organisatieniveau uitvoeren "
            "(SIRA - Systematic Integrity Risk Assessment). Dit omvat:\n\n"
            "- Identificatie van risicofactoren (cliënttype, diensten, landen, transacties)\n"
            "- Classificatie van risico's (laag, normaal, hoog)\n"
            "- Beschrijving van beheersmaatregelen per risicocategorie\n"
            "- Procedures voor escalatie en besluitvorming\n"
            "- Jaarlijkse evaluatie en actualisering van het risicobeleid\n\n"
            "Het BFT beoordeelt de kwaliteit van het risicobeleid bij inspecties."
        ),
    },
    {
        "key": "pep_sancties",
        "title": "PEP, sancties en herkomst middelen",
        "order": 3,
        "office_action_required": True,
        "office_action_description": (
            "Controleer bij elke nieuwe cliënt en periodiek of de cliënt of UBO een PEP is, "
            "op een sanctielijst staat, of dat er negatieve berichtgeving is. Documenteer de "
            "uitkomst en onderneem actie bij positieve hits."
        ),
        "body": (
            "De Wwft vereist verscherpte aandacht voor:\n\n"
            "PEP-screening (Politically Exposed Persons):\n"
            "- Binnenlandse en buitenlandse PEP's en hun familieleden/naaste geassocieerden\n"
            "- Bronnen: Almanak der Eerste en Tweede Kamer, EU/internationaal\n\n"
            "Sanctiescreening:\n"
            "- EU Consolidated Sanctions List\n"
            "- Nationaal sanctieoverzicht (Rijksoverheid)\n"
            "- VN Security Council Consolidated List\n\n"
            "Herkomst middelen:\n"
            "- Bij hoog risico: onderzoek naar herkomst van het vermogen\n"
            "- Documentatie van vermogensbronnen in het dossier"
        ),
    },
    {
        "key": "verscherpt_onderzoek",
        "title": "Verscherpt cliëntenonderzoek",
        "order": 4,
        "office_action_required": True,
        "office_action_description": (
            "Bij verhoogd risico (PEP, hoog-risicoland, complexe structuren) moet verscherpt "
            "cliëntenonderzoek worden toegepast. Documenteer de aanvullende maatregelen en "
            "laat een senior medewerker de relatie goedkeuren."
        ),
        "body": (
            "Verscherpt cliëntenonderzoek (EDD - Enhanced Due Diligence) is verplicht wanneer:\n\n"
            "- De cliënt of UBO een PEP is (art. 8 Wwft)\n"
            "- De cliënt gevestigd is in een hoog-risicoland (EU-lijst/FATF)\n"
            "- Er sprake is van complexe of ongebruikelijke transactiepatronen\n"
            "- Correspondent-bankrelaties met derde landen\n"
            "- De risicobeoordeling een verhoogd risico aangeeft\n\n"
            "Aanvullende maatregelen omvatten:\n"
            "- Goedkeuring door hoger management\n"
            "- Vaststelling bron van vermogen en middelen\n"
            "- Intensievere monitoring van de zakelijke relatie"
        ),
    },
    {
        "key": "meldplicht",
        "title": "Meldplicht en transactiemonitoring",
        "order": 5,
        "office_action_required": True,
        "office_action_description": (
            "Het kantoor is verplicht ongebruikelijke transacties te melden bij de FIU-Nederland. "
            "Zorg dat medewerkers de indicatoren kennen en dat er een interne meldprocedure is. "
            "De melding moet 'zo spoedig mogelijk' na het constateren worden gedaan."
        ),
        "body": (
            "De meldplicht is een kernverplichting onder de Wwft:\n\n"
            "1. Elke ongebruikelijke transactie moet worden gemeld bij FIU-Nederland\n"
            "2. Melding via het FIU-portaal (goAML) - zo spoedig mogelijk\n"
            "3. Tipping-off verbod: de cliënt mag niet worden geïnformeerd over de melding\n"
            "4. Bewaarplicht: meldingen en onderliggende stukken 5 jaar bewaren\n\n"
            "Objectieve indicatoren (verplichte melding):\n"
            "- Contante transacties boven € 15.000\n"
            "- Witwas- of terrorismefinancieringsindicatoren\n\n"
            "Subjectieve indicatoren:\n"
            "- Transacties waarbij aanleiding is om te vermoeden dat ze verband houden met witwassen of terrorismefinanciering"
        ),
    },
    {
        "key": "herbeoordeling",
        "title": "Periodieke herbeoordeling",
        "order": 6,
        "office_action_required": True,
        "office_action_description": (
            "Plan periodieke herbeoordelingen van bestaande cliëntrelaties: jaarlijks voor "
            "hoog risico, elke 3 jaar voor normaal risico, elke 5 jaar voor laag risico. "
            "Actualiseer het cliëntdossier bij elke herbeoordeling."
        ),
        "body": (
            "Voortdurende controle (ongoing monitoring) is een wettelijke verplichting:\n\n"
            "- Regelmatige herbeoordeling van het risicoprofiel van de cliënt\n"
            "- Controle of de transacties overeenkomen met de kennis van de cliënt\n"
            "- Actualisering van CDD-documenten\n\n"
            "Aanbevolen frequentie:\n"
            "- Hoog risico: jaarlijks\n"
            "- Normaal risico: elke 3 jaar\n"
            "- Laag risico: elke 5 jaar\n"
            "- Event-driven: bij materiële wijzigingen in de relatie"
        ),
    },
    {
        "key": "compliance_infra",
        "title": "Intern compliance-infrastructuur",
        "order": 7,
        "office_action_required": True,
        "office_action_description": (
            "Wijs een compliance officer aan, zorg voor adequate Wwft-training van alle "
            "medewerkers (minimaal jaarlijks), en richt een intern meld- en escalatieproces in."
        ),
        "body": (
            "Een effectieve compliance-infrastructuur omvat:\n\n"
            "Compliance functie:\n"
            "- Aangewezen compliance officer (of verantwoordelijke bij klein kantoor)\n"
            "- Onafhankelijke positie met directe rapportagelijn naar bestuur\n"
            "- Bevoegdheid om zakelijke relaties te weigeren of beëindigen\n\n"
            "Opleiding en bewustwording:\n"
            "- Jaarlijkse Wwft-training voor alle medewerkers\n"
            "- Documentatie van trainingen (inhoud, deelnemers, datum)\n"
            "- Actualisering bij wetswijzigingen\n\n"
            "Intern beleid en procedures:\n"
            "- Schriftelijke procedures voor CDD, meldplicht, escalatie\n"
            "- Integriteitsbeleid en gedragscode\n"
            "- Audit trail en dossiervorming"
        ),
    },
    {
        "key": "bft_bevindingen",
        "title": "BFT inspectie-bevindingen",
        "order": 8,
        "office_action_required": False,
        "body": (
            "Het Bureau Financieel Toezicht (BFT) houdt toezicht op de naleving van de Wwft "
            "door onder meer accountants, belastingadviseurs en notarissen.\n\n"
            "Veelvoorkomende BFT-bevindingen:\n"
            "- Onvoldoende of ontbrekend cliëntenonderzoek\n"
            "- Geen of onvolledig risicobeleid (SIRA)\n"
            "- Ontbreken van PEP- en sanctiescreening\n"
            "- Niet melden van ongebruikelijke transacties\n"
            "- Onvoldoende training van medewerkers\n"
            "- Gebrekkige dossiervorming\n\n"
            "Sancties bij overtreding variëren van een waarschuwing tot boetes en "
            "tuchtrechtelijke maatregelen. Het BFT publiceert jaarlijks een toezichtrapport "
            "met aandachtspunten voor de beroepsgroepen."
        ),
    },
    {
        "key": "actuele_wetgeving",
        "title": "Actuele wet- en regelgeving",
        "order": 9,
        "office_action_required": False,
        "body": (
            "Overzicht van recente en aankomende wijzigingen in WWFT-gerelateerde wetgeving:\n\n"
            "- Implementatie EU Anti-Money Laundering Package (AMLR/AMLD6)\n"
            "- Oprichting EU Anti-Money Laundering Authority (AMLA)\n"
            "- Wijzigingen UBO-register en toegankelijkheid\n"
            "- Actualisering sanctieregelgeving\n"
            "- FIU-Nederland: nieuwe typologieën en leidraden\n"
            "- BFT: toezichtprioriteiten en beleidsregels\n\n"
            "Gebruik de zoekfunctie hieronder om specifieke wetgeving op te zoeken."
        ),
    },
]


def seed_sections(apps, schema_editor):
    ComplianceSection = apps.get_model("dashboard", "ComplianceSection")
    for data in SECTIONS:
        ComplianceSection.objects.update_or_create(
            key=data["key"],
            defaults={
                "title": data["title"],
                "body": data["body"],
                "order": data["order"],
                "office_action_required": data.get("office_action_required", False),
                "office_action_description": data.get("office_action_description", ""),
            },
        )


def unseed_sections(apps, schema_editor):
    ComplianceSection = apps.get_model("dashboard", "ComplianceSection")
    ComplianceSection.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0009_add_compliance_section"),
    ]

    operations = [
        migrations.RunPython(seed_sections, unseed_sections),
    ]
