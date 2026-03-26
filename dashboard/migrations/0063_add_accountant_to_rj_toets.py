"""Add Accountant agent and task to the RJ Verslaggevingstoets team."""

from django.db import migrations


def add_accountant(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")

    team = Team.objects.filter(slug="rj-verslaggevingstoets").first()
    if not team:
        return

    # Find the existing RJ task (order=1) for context dependency
    rj_task = TeamTask.objects.filter(team=team, order=1).first()

    # --- Agent: Accountant ---
    accountant = TeamAgent.objects.create(
        team=team,
        order=2,
        role="Accountant — Beoordelaar & Adviseur",
        goal=(
            "Beoordeel als registeraccountant de werkzaamheden van de RJ "
            "Verslaggevingscontroleur. Interpreteer de bevindingen, maak "
            "definitieve professionele oordelen en stel een concreet, actionable "
            "rapport op: welke posten moeten worden aangepast, welke toelichtingen "
            "aangevuld of herschreven, welke waarderingsgrondslagen herzien, en "
            "welke presentatiewijzigingen nodig zijn. Prioriteer op materialiteit "
            "en urgentie. Schrijf in het Nederlands."
        ),
        backstory=(
            "Je bent een ervaren registeraccountant (RA) met jarenlange "
            "praktijkervaring in het samenstellen en beoordelen van jaarrekeningen "
            "van MKB-ondernemingen. Je maakt heldere, onderbouwde keuzes en "
            "formuleert advies dat direct uitvoerbaar is. Je focust op wat echt "
            "toe doet: niet alleen technische RJ-naleving maar ook bruikbaarheid "
            "voor stakeholders."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-pro",
        tools=["rj_lookup"],
        max_iter=30,
        verbose=True,
    )

    # --- Task: Accountantsbeoordeling ---
    accountant_task = TeamTask.objects.create(
        team=team,
        order=2,
        description=(
            "Beoordeel als accountant het rapport van de RJ "
            "Verslaggevingscontroleur en stel een definitief adviesrapport op:\n\n"
            "# 1. Professioneel oordeel\n"
            "Geef je overall oordeel over de jaarrekening: geeft deze een "
            "getrouw beeld? Waar zitten de belangrijkste risico's?\n\n"
            "# 2. Verplichte aanpassingen\n"
            "Per niet-conforme bevinding uit het rapport van de "
            "Verslaggevingscontroleur:\n"
            "- Wat moet er concreet worden aangepast in de jaarrekening?\n"
            "- In welke post/toelichting/bijlage?\n"
            "- Wat is de impact (materieel/niet-materieel)?\n"
            "- Urgentie: hoog/midden/laag\n\n"
            "# 3. Aanbevolen verbeteringen\n"
            "Verbeteringen die niet strikt verplicht zijn maar de kwaliteit "
            "van de jaarrekening verhogen.\n\n"
            "# 4. Ontbrekende toelichtingen\n"
            "Welke toelichtingen moeten worden toegevoegd? Lever waar "
            "mogelijk een concepttekst.\n\n"
            "# 5. Samenvatting voor de klant\n"
            "Een beknopt, begrijpelijk overzicht (max 1 A4) dat je aan de "
            "ondernemer kunt overhandigen.\n\n"
            "Gebruik de RJ Richtlijnen Lookup tool om je verwijzingen te "
            "verifiëren. Schrijf in het Nederlands."
        ),
        expected_output=(
            "Een compleet accountantsadviesrapport met geprioriteerde "
            "aanpassingslijst per jaarrekeningpost en een klantgerichte "
            "samenvatting."
        ),
        agent=accountant,
    )

    if rj_task:
        accountant_task.context_tasks.add(rj_task)


def reverse_accountant(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamAgent.objects.filter(
        team__slug="rj-verslaggevingstoets",
        role="Accountant — Beoordelaar & Adviseur",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0062_seed_rj_verslaggevingstoets"),
    ]

    operations = [
        migrations.RunPython(add_accountant, reverse_accountant),
    ]
