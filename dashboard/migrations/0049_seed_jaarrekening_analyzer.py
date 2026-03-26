"""Seed the Jaarrekening Analyzer team with variable, agents and tasks."""

from django.db import migrations


def seed_jaarrekening_analyzer(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamVariable = apps.get_model("dashboard", "TeamVariable")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")

    team = Team.objects.filter(slug="jaarrekening-analyzer").first()
    if not team:
        team = Team.objects.create(
            name="Jaarrekening Analyzer",
            slug="jaarrekening-analyzer",
            description="Analyseert een jaarrekening-PDF: OCR-extractie, fiscale analyse, bedrijfseconomische analyse en verslaggevingscontrole.",
            process="sequential",
            verbose=True,
        )

    # Clean up existing agents/tasks/variables
    team.agents.all().delete()  # cascade deletes tasks too
    team.variables.all().delete()

    # --- Variable: file upload ---
    TeamVariable.objects.create(
        team=team,
        name="jaarrekening_path",
        label="Jaarrekening PDF",
        description="Upload de jaarrekening als PDF-bestand voor analyse.",
        input_type="file_path",
        default_value="",
        required=True,
        order=0,
    )

    # --- Agents ---
    ocr_agent = TeamAgent.objects.create(
        team=team,
        order=0,
        role="Jaarrekening OCR Specialist",
        goal="Lees de jaarrekening PDF in via '{jaarrekening_path}' met OCR en lever de volledige tekst op als gestructureerde markdown. Behoud de oorspronkelijke structuur: balans, winst-en-verliesrekening, kasstroomoverzicht, toelichting en overige bijlagen.",
        backstory="Je bent een documentspecialist die getraind is in het verwerken van financiële documenten. Je herkent tabellen, cijfers en structuren in jaarrekeningen feilloos en levert altijd een nauwkeurige, leesbare tekstversie op.",
        llm_provider="gemini",
        llm_model="gemini-3.1-flash",
        tools=["mistral_ocr"],
        max_iter=10,
        verbose=True,
    )

    fiscaal_agent = TeamAgent.objects.create(
        team=team,
        order=1,
        role="Fiscaal Analist",
        goal="Analyseer de jaarrekening op alle fiscale aspecten. Beoordeel: vennootschapsbelasting (effectieve druk, latente belastingen, verliescompensatie), btw-positie, loonheffingen, investeringsaftrek (KIA/EIA/MIA/VAMIL), innovatiebox, en andere fiscale faciliteiten. Signaleer risico's en optimalisatiemogelijkheden. Schrijf in het Nederlands.",
        backstory="Je bent een ervaren fiscalist met diepgaande kennis van het Nederlandse belastingstelsel. Je kunt uit een jaarrekening alle fiscale implicaties destilleren en praktische adviezen formuleren voor ondernemers en hun adviseurs.",
        llm_provider="gemini",
        llm_model="gemini-3.1-pro",
        tools=[],
        max_iter=30,
        verbose=True,
    )

    bedrijfsecon_agent = TeamAgent.objects.create(
        team=team,
        order=2,
        role="Bedrijfseconomisch Analist",
        goal="Voer een bedrijfseconomische analyse uit op de jaarrekening. Bereken en beoordeel: liquiditeitsratio's (current/quick ratio), solvabiliteit (debt-to-equity), rentabiliteit (REV/RTV/RVV), werkkapitaal, cashflow, omzetgroei, kostenstructuur en winstmarges. Vergelijk waar mogelijk met sectorgemiddelden. Signaleer trends en aandachtspunten. Schrijf in het Nederlands.",
        backstory="Je bent een bedrijfseconoom gespecialiseerd in financiële analyse van MKB-ondernemingen. Je vertaalt droge cijfers naar inzichtelijke analyses die ondernemers en adviseurs direct kunnen gebruiken voor besluitvorming.",
        llm_provider="gemini",
        llm_model="gemini-3.1-pro",
        tools=[],
        max_iter=30,
        verbose=True,
    )

    verslaggeving_agent = TeamAgent.objects.create(
        team=team,
        order=3,
        role="Verslaggevingscontroleur",
        goal="Controleer de jaarrekening op naleving van de Richtlijnen voor de Jaarverslaggeving (RJ). Beoordeel: presentatie en rubricering, volledigheid van toelichtingen, waarderingsgrondslagen, continuïteitsveronderstelling, materialiteit, en naleving van specifieke RJ-richtlijnen. Stel een eindrapport op dat alle bevindingen van het team samenvat met een overzichtelijke conclusie en aanbevelingen. Schrijf in het Nederlands.",
        backstory="Je bent een senior accountant met jarenlange ervaring in de controle van jaarrekeningen volgens Nederlandse verslaggevingsstandaarden. Je kent de RJ-richtlijnen uit je hoofd en kunt snel beoordelen of een jaarrekening aan alle eisen voldoet.",
        llm_provider="gemini",
        llm_model="gemini-3.1-pro",
        tools=[],
        max_iter=30,
        verbose=True,
    )

    # --- Tasks ---
    ocr_task = TeamTask.objects.create(
        team=team,
        order=0,
        description="Lees de jaarrekening PDF in via '{jaarrekening_path}' met de Mistral OCR tool. Lever de volledige tekst op als gestructureerde markdown met behoud van:\n- Balans (activa en passiva)\n- Winst-en-verliesrekening\n- Kasstroomoverzicht (indien aanwezig)\n- Toelichting op de jaarrekening\n- Overige bijlagen",
        expected_output="De volledige tekst van de jaarrekening in gestructureerde markdown, met alle financiële tabellen, cijfers en toelichtingen nauwkeurig overgenomen.",
        agent=ocr_agent,
    )

    fiscaal_task = TeamTask.objects.create(
        team=team,
        order=1,
        description="Analyseer de jaarrekening op fiscale aspecten:\n\n1. Vennootschapsbelasting: effectieve belastingdruk, latente belastingvorderingen/-verplichtingen, verliescompensatie\n2. Btw-positie: voorbelasting, afdracht, eventuele correcties\n3. Loonheffingen: personeelskosten in relatie tot loonsom\n4. Investeringsaftrek: KIA, EIA, MIA, VAMIL-mogelijkheden\n5. Innovatiebox en overige faciliteiten\n6. Fiscale risico's en aandachtspunten\n7. Optimalisatiemogelijkheden\n\nSchrijf in het Nederlands.",
        expected_output="Een gestructureerd fiscaal analyserapport met per onderwerp de bevindingen, risico-inschatting en concrete aanbevelingen.",
        agent=fiscaal_agent,
    )
    fiscaal_task.context_tasks.add(ocr_task)

    bedrijfsecon_task = TeamTask.objects.create(
        team=team,
        order=2,
        description="Voer een bedrijfseconomische analyse uit:\n\n1. Liquiditeit: current ratio, quick ratio, werkkapitaal\n2. Solvabiliteit: debt-to-equity ratio, interest coverage\n3. Rentabiliteit: REV, RTV, RVV, bruto/netto winstmarge\n4. Activiteit: omloopsnelheid voorraden, debiteurentermijn, crediteurentermijn\n5. Cashflow-analyse: operationele, investerings- en financieringscashflow\n6. Trendanalyse: vergelijking met voorgaand jaar (indien beschikbaar)\n7. Aandachtspunten en risico's\n\nSchrijf in het Nederlands.",
        expected_output="Een bedrijfseconomisch analyserapport met berekende kengetallen, beoordeling per categorie en een samenvattende conclusie over de financiële gezondheid.",
        agent=bedrijfsecon_agent,
    )
    bedrijfsecon_task.context_tasks.add(ocr_task)

    verslaggeving_task = TeamTask.objects.create(
        team=team,
        order=3,
        description="Controleer de jaarrekening op verslaggevingskwaliteit en stel het eindrapport op:\n\n1. RJ-naleving: presentatie, rubricering, waarderingsgrondslagen\n2. Volledigheid toelichtingen: zijn alle vereiste toelichtingen aanwezig?\n3. Continuïteit: zijn er signalen die de continuïteit bedreigen?\n4. Materialiteit: zijn er materiële afwijkingen?\n5. Consistentie: zijn grondslagen consistent toegepast?\n\nCompileer vervolgens ALLE bevindingen (OCR, fiscaal, bedrijfseconomisch, verslaggeving) tot één overzichtelijk eindrapport met:\n- Management samenvatting\n- Fiscale bevindingen en aanbevelingen\n- Bedrijfseconomische analyse en kengetallen\n- Verslaggevingsbevindingen\n- Algehele conclusie en prioriteiten\n\nSchrijf in het Nederlands.",
        expected_output="Een compleet eindrapport van de jaarrekening-analyse met alle deelanalyses geïntegreerd, inclusief management samenvatting, concrete bevindingen per categorie en geprioriteerde aanbevelingen.",
        agent=verslaggeving_agent,
    )
    verslaggeving_task.context_tasks.add(ocr_task)
    verslaggeving_task.context_tasks.add(fiscaal_task)
    verslaggeving_task.context_tasks.add(bedrijfsecon_task)


def reverse_seed(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    team = Team.objects.filter(slug="jaarrekening-analyzer").first()
    if team:
        team.agents.all().delete()
        team.variables.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0048_seed_historical_api_usage"),
    ]

    operations = [
        migrations.RunPython(seed_jaarrekening_analyzer, reverse_seed),
    ]
