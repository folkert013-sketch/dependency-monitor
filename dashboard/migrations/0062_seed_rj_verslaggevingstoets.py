"""Seed het RJ Verslaggevingstoets team met OCR + RJ Lookup agents."""

from django.db import migrations


def seed_rj_toets_team(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamVariable = apps.get_model("dashboard", "TeamVariable")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")

    team = Team.objects.filter(slug="rj-verslaggevingstoets").first()
    if not team:
        team = Team.objects.create(
            name="RJ Verslaggevingstoets",
            slug="rj-verslaggevingstoets",
            description=(
                "Toetst een jaarrekening aan de Richtlijnen voor de Jaarverslaggeving (RJ) "
                "voor micro- en kleine rechtspersonen. Levert een analyserapport met "
                "bevindingen per rubriek en concrete acties."
            ),
            process="sequential",
            verbose=True,
        )

    # Opschonen
    team.agents.all().delete()
    team.variables.all().delete()

    # --- Variable ---
    TeamVariable.objects.create(
        team=team,
        name="jaarrekening_path",
        label="Jaarrekening PDF",
        description="Upload de jaarrekening als PDF-bestand voor RJ-toetsing.",
        input_type="file_path",
        default_value="",
        required=True,
        order=0,
    )

    # --- Agent 1: OCR Specialist ---
    ocr_agent = TeamAgent.objects.create(
        team=team,
        order=0,
        role="Jaarrekening OCR Specialist",
        goal=(
            "Lees de jaarrekening PDF in via '{jaarrekening_path}' met OCR en "
            "lever de volledige tekst op als gestructureerde markdown. Behoud de "
            "oorspronkelijke structuur: balans, winst-en-verliesrekening, "
            "toelichting en overige bijlagen."
        ),
        backstory=(
            "Je bent een documentspecialist getraind in het verwerken van "
            "financiële documenten. Je herkent tabellen, cijfers en structuren "
            "in jaarrekeningen feilloos."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-flash",
        tools=["mistral_ocr"],
        max_iter=10,
        verbose=True,
    )

    # --- Agent 2: RJ Verslaggevingscontroleur ---
    rj_agent = TeamAgent.objects.create(
        team=team,
        order=1,
        role="RJ Verslaggevingscontroleur",
        goal=(
            "Toets de jaarrekening systematisch aan de Richtlijnen voor de "
            "Jaarverslaggeving (RJ) voor micro- en kleine rechtspersonen. "
            "Gebruik de RJ Richtlijnen Lookup tool om per rubriek de specifieke "
            "bepalingen op te zoeken. Controleer waarderingsgrondslagen, "
            "presentatie, rubricering en volledigheid van toelichtingen. "
            "Lever een gestructureerd rapport op met analyse én concrete acties. "
            "Schrijf in het Nederlands."
        ),
        backstory=(
            "Je bent een senior accountant met jarenlange ervaring in de "
            "controle van jaarrekeningen volgens Nederlandse "
            "verslaggevingsstandaarden. Je toetst methodisch elke rubriek "
            "in de jaarrekening aan de relevante RJ-richtlijnen en formuleert "
            "heldere, actiegerichte bevindingen."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-pro",
        tools=["rj_lookup"],
        max_iter=40,
        verbose=True,
    )

    # --- Taak 1: OCR Extractie ---
    ocr_task = TeamTask.objects.create(
        team=team,
        order=0,
        description=(
            "Lees de jaarrekening PDF in via '{jaarrekening_path}' met de "
            "Mistral OCR tool. Lever de volledige tekst op als gestructureerde "
            "markdown met behoud van:\n"
            "- Balans (activa en passiva)\n"
            "- Winst-en-verliesrekening\n"
            "- Toelichting op de jaarrekening\n"
            "- Waarderingsgrondslagen\n"
            "- Overige bijlagen"
        ),
        expected_output=(
            "De volledige tekst van de jaarrekening in gestructureerde markdown, "
            "met alle financiële tabellen, cijfers en toelichtingen nauwkeurig "
            "overgenomen."
        ),
        agent=ocr_agent,
    )

    # --- Taak 2: RJ Toetsing ---
    rj_task = TeamTask.objects.create(
        team=team,
        order=1,
        description=(
            "Toets de jaarrekening per rubriek aan de RJ-richtlijnen. "
            "Gebruik de RJ Richtlijnen Lookup tool om per rubriek de "
            "specifieke bepalingen op te zoeken.\n\n"
            "Doorloop minimaal de volgende rubrieken (voor zover aanwezig "
            "in de jaarrekening):\n"
            "- Immateriële vaste activa (zoek: B1)\n"
            "- Materiële vaste activa (zoek: materiële vaste activa)\n"
            "- Financiële vaste activa (zoek: B3)\n"
            "- Voorraden (zoek: voorraden)\n"
            "- Vorderingen (zoek: vorderingen)\n"
            "- Liquide middelen (zoek: liquide middelen)\n"
            "- Eigen vermogen (zoek: eigen vermogen)\n"
            "- Voorzieningen (zoek: voorzieningen)\n"
            "- Schulden (zoek: schulden)\n"
            "- Winst-en-verliesrekening (zoek: B13)\n"
            "- Personeelsbeloningen (zoek: personeelsbeloningen)\n"
            "- Belastingen naar de winst (zoek: B15)\n\n"
            "Structureer het rapport als volgt:\n\n"
            "# DEEL 1 — ANALYSE\n\n"
            "Per rubriek:\n"
            "| Rubriek | RJ-code | Bevinding | RJ-vereiste (alinea ref) | Oordeel |\n"
            "Oordeel: ✅ Conform / ❌ Niet-conform / ⚠️ Aandachtspunt\n\n"
            "# DEEL 2 — ACTIES\n\n"
            "## Correcties (Hoog)\n"
            "Concrete aanpassingen die nodig zijn om aan de RJ te voldoen.\n\n"
            "## Aandachtspunten (Midden)\n"
            "Zaken die aandacht verdienen maar niet per se fout zijn.\n\n"
            "## Ontbrekende toelichtingen (Hoog/Midden)\n"
            "Toelichtingen die volgens de RJ vereist zijn maar ontbreken.\n\n"
            "## Overige opmerkingen (Laag)\n"
            "Suggesties voor verbetering van de verslaggeving."
        ),
        expected_output=(
            "Een gestructureerd RJ-toetsingsrapport met:\n"
            "- Deel 1: Analyse per rubriek met bevindingen, RJ-referenties en oordeel\n"
            "- Deel 2: Acties onderverdeeld in correcties, aandachtspunten, "
            "ontbrekende toelichtingen en overige opmerkingen, elk met prioriteit"
        ),
        agent=rj_agent,
    )
    rj_task.context_tasks.add(ocr_task)


def reverse_seed(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    team = Team.objects.filter(slug="rj-verslaggevingstoets").first()
    if team:
        team.agents.all().delete()
        team.variables.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0061_add_rj_tool_to_analyzer"),
    ]

    operations = [
        migrations.RunPython(seed_rj_toets_team, reverse_seed),
    ]
