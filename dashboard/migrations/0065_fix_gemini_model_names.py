"""Fix non-existent Gemini model IDs to actual available models."""

from django.db import migrations


def fix_model_names(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")

    # gemini-3.1-flash does not exist, use gemini-2.5-flash
    TeamAgent.objects.filter(
        llm_provider="gemini", llm_model="gemini-3.1-flash"
    ).update(llm_model="gemini-2.5-flash")

    # gemini-3.1-pro does not exist, use gemini-2.5-pro
    TeamAgent.objects.filter(
        llm_provider="gemini", llm_model="gemini-3.1-pro"
    ).update(llm_model="gemini-2.5-pro")

    # gemini-3.1-flash-lite does not exist, use gemini-3.1-flash-lite-preview
    TeamAgent.objects.filter(
        llm_provider="gemini", llm_model="gemini-3.1-flash-lite"
    ).update(llm_model="gemini-3.1-flash-lite-preview")


def reverse_fix(apps, schema_editor):
    pass  # No reverse needed


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0064_add_task_output_model"),
    ]

    operations = [
        migrations.RunPython(fix_model_names, reverse_fix),
    ]
