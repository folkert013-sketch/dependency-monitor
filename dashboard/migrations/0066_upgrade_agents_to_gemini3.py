"""Upgrade all Gemini 2.x agents to Gemini 3.x models."""

from django.db import migrations


def upgrade_to_gemini3(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")

    TeamAgent.objects.filter(
        llm_provider="gemini", llm_model="gemini-2.5-flash"
    ).update(llm_model="gemini-3.1-flash-lite-preview")

    TeamAgent.objects.filter(
        llm_provider="gemini", llm_model="gemini-2.5-pro"
    ).update(llm_model="gemini-3.1-pro-preview")

    TeamAgent.objects.filter(
        llm_provider="gemini", llm_model="gemini-2.0-flash"
    ).update(llm_model="gemini-3-flash-preview")


def reverse_upgrade(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0065_fix_gemini_model_names"),
    ]

    operations = [
        migrations.RunPython(upgrade_to_gemini3, reverse_upgrade),
    ]
