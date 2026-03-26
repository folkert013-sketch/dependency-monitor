"""Add rj_lookup tool to the Verslaggevingscontroleur agent in the Jaarrekening Analyzer team."""

from django.db import migrations


def add_rj_tool(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")

    # Zoek de Verslaggevingscontroleur agent
    agent = TeamAgent.objects.filter(
        team__slug="jaarrekening-analyzer",
        role="Verslaggevingscontroleur",
    ).first()

    if not agent:
        return

    # Voeg rj_lookup toe aan tools als het er nog niet in staat
    tools = agent.tools or []
    if "rj_lookup" not in tools:
        tools.append("rj_lookup")
        agent.tools = tools

    # Update goal met expliciete instructie om de tool te gebruiken
    agent.goal = (
        "Controleer de jaarrekening op naleving van de Richtlijnen voor de "
        "Jaarverslaggeving (RJ). Gebruik de RJ Richtlijnen Lookup tool om per "
        "rubriek (bijv. materiële vaste activa, voorraden, eigen vermogen) de "
        "specifieke RJ-bepalingen op te zoeken. Beoordeel: presentatie en "
        "rubricering, volledigheid van toelichtingen, waarderingsgrondslagen, "
        "continuïteitsveronderstelling, materialiteit, en naleving van "
        "specifieke RJ-richtlijnen. Stel een eindrapport op dat alle "
        "bevindingen van het team samenvat met een overzichtelijke conclusie "
        "en aanbevelingen. Schrijf in het Nederlands."
    )
    agent.save()


def reverse_rj_tool(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    agent = TeamAgent.objects.filter(
        team__slug="jaarrekening-analyzer",
        role="Verslaggevingscontroleur",
    ).first()
    if agent:
        tools = agent.tools or []
        if "rj_lookup" in tools:
            tools.remove("rj_lookup")
            agent.tools = tools
            agent.save()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0060_add_rj_models"),
    ]

    operations = [
        migrations.RunPython(add_rj_tool, reverse_rj_tool),
    ]
