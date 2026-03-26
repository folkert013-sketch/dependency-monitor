"""Fix Kwaliteitsmanager model name: gemini-3.1-pro does not exist,
the correct ID is gemini-3.1-pro-preview."""

from django.db import migrations


def fix_model_name(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamAgent.objects.filter(
        llm_provider="gemini", llm_model="gemini-3.1-pro"
    ).update(llm_model="gemini-3.1-pro-preview")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0074_fix_manager_tools"),
    ]

    operations = [
        migrations.RunPython(fix_model_name, noop),
    ]
