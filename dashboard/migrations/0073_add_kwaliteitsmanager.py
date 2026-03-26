"""Add Kwaliteitsmanager (sparringpartner) to RJ Verslaggevingstoets
and switch team to hierarchical process."""

from django.db import migrations


def add_kwaliteitsmanager(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")

    team = Team.objects.filter(slug="rj-verslaggevingstoets").first()
    if not team:
        return

    # Switch to hierarchical process
    team.process = "hierarchical"
    team.save(update_fields=["process"])

    # Add Kwaliteitsmanager as manager agent
    TeamAgent.objects.create(
        team=team,
        order=3,
        role="Kwaliteitsmanager — Sparringpartner",
        goal=(
            "Kritische sparringpartner die de kwaliteit van rapportages "
            "bewaakt. Controleert weergave, uitlijning, consistentie en "
            "leesbaarheid. Laat werk pas door wanneer het aan professionele "
            "standaarden voldoet."
        ),
        backstory=(
            "Je bent een ervaren quality controller met een scherp oog "
            "voor detail. Je beoordeelt niet alleen de inhoud maar vooral "
            "de presentatie: zijn de rapporten helder gestructureerd, "
            "consistent opgemaakt en professioneel leesbaar? Je geeft "
            "constructieve feedback en werkt samen met de andere agenten "
            "tot het resultaat optimaal is."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-pro",
        tools=["markdown_to_pdf"],
        max_iter=20,
        verbose=True,
        is_manager=True,
    )


def reverse_kwaliteitsmanager(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")

    team = Team.objects.filter(slug="rj-verslaggevingstoets").first()
    if not team:
        return

    # Restore sequential process
    team.process = "sequential"
    team.save(update_fields=["process"])

    # Remove the manager agent
    TeamAgent.objects.filter(
        team=team,
        is_manager=True,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0072_cleanup_rj_agent_goals"),
    ]

    operations = [
        migrations.RunPython(add_kwaliteitsmanager, reverse_kwaliteitsmanager),
    ]
