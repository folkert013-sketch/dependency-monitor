"""Clean up RJ Verslaggevingstoets agent goals (dispositie i.p.v. instructies)
and add markdown_to_pdf tool to all agents."""

from django.db import migrations


PDF_INSTRUCTION = (
    "\n\nGenereer tot slot een PDF-rapport van je output "
    "met de Markdown naar PDF tool."
)

# New dispositie-focused goals
NEW_GOALS = {
    0: (
        "Nauwkeurige documentspecialist die financiele documenten feilloos "
        "digitaliseert. Staat garant voor volledigheid zonder informatieverlies."
    ),
    1: (
        "Methodische expert in Nederlandse verslaggevingsstandaarden (RJ) "
        "voor micro- en kleine rechtspersonen. Grondig, nauwkeurig en altijd "
        "onderbouwd met concrete RJ-referenties."
    ),
    2: (
        "Ervaren registeraccountant met focus op praktisch, uitvoerbaar "
        "advies. Beoordeelt bevindingen op materialiteit en vertaalt deze "
        "naar concrete acties voor de klant."
    ),
}

# Original goals for reverse migration
ORIGINAL_GOALS = {
    0: (
        "Lees de jaarrekening PDF in via '{jaarrekening_path}' met OCR en "
        "lever de volledige tekst op als gestructureerde markdown. Behoud de "
        "oorspronkelijke structuur: balans, winst-en-verliesrekening, "
        "toelichting en overige bijlagen."
    ),
    1: (
        "Toets de jaarrekening systematisch aan de Richtlijnen voor de "
        "Jaarverslaggeving (RJ) voor micro- en kleine rechtspersonen. "
        "Gebruik de RJ Richtlijnen Lookup tool om per rubriek de specifieke "
        "bepalingen op te zoeken. Controleer waarderingsgrondslagen, "
        "presentatie, rubricering en volledigheid van toelichtingen. "
        "Lever een gestructureerd rapport op met analyse én concrete acties. "
        "Schrijf in het Nederlands."
    ),
    2: (
        "Beoordeel als registeraccountant de werkzaamheden van de RJ "
        "Verslaggevingscontroleur. Interpreteer de bevindingen, maak "
        "definitieve professionele oordelen en stel een concreet, actionable "
        "rapport op: welke posten moeten worden aangepast, welke toelichtingen "
        "aangevuld of herschreven, welke waarderingsgrondslagen herzien, en "
        "welke presentatiewijzigingen nodig zijn. Prioriteer op materialiteit "
        "en urgentie. Schrijf in het Nederlands."
    ),
}

# Original tools per agent order
ORIGINAL_TOOLS = {
    0: ["mistral_ocr"],
    1: ["rj_lookup"],
    2: ["rj_lookup"],
}

# New tools (markdown_to_pdf added)
NEW_TOOLS = {
    0: ["mistral_ocr", "markdown_to_pdf"],
    1: ["rj_lookup", "markdown_to_pdf"],
    2: ["rj_lookup", "markdown_to_pdf"],
}


def update_agents_and_tasks(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")

    agents = TeamAgent.objects.filter(
        team__slug="rj-verslaggevingstoets"
    ).order_by("order")

    for agent in agents:
        if agent.order in NEW_GOALS:
            agent.goal = NEW_GOALS[agent.order]
            agent.tools = NEW_TOOLS[agent.order]
            agent.save(update_fields=["goal", "tools"])

    tasks = TeamTask.objects.filter(
        team__slug="rj-verslaggevingstoets"
    ).order_by("order")

    for task in tasks:
        if not task.description.endswith(PDF_INSTRUCTION.strip()):
            task.description = task.description + PDF_INSTRUCTION
            task.save(update_fields=["description"])


def reverse_agents_and_tasks(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")

    agents = TeamAgent.objects.filter(
        team__slug="rj-verslaggevingstoets"
    ).order_by("order")

    for agent in agents:
        if agent.order in ORIGINAL_GOALS:
            agent.goal = ORIGINAL_GOALS[agent.order]
            agent.tools = ORIGINAL_TOOLS[agent.order]
            agent.save(update_fields=["goal", "tools"])

    tasks = TeamTask.objects.filter(
        team__slug="rj-verslaggevingstoets"
    ).order_by("order")

    for task in tasks:
        if task.description.endswith(PDF_INSTRUCTION):
            task.description = task.description[: -len(PDF_INSTRUCTION)]
            task.save(update_fields=["description"])


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0071_update_kort_and_add_agentic_header"),
    ]

    operations = [
        migrations.RunPython(update_agents_and_tasks, reverse_agents_and_tasks),
    ]
