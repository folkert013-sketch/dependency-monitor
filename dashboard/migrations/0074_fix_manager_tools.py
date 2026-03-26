"""Remove tools from manager agents — CrewAI hierarchical process
does not allow the manager agent to have tools."""

from django.db import migrations


def clear_manager_tools(apps, schema_editor):
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamAgent.objects.filter(is_manager=True).exclude(tools=[]).update(tools=[])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0073_add_kwaliteitsmanager"),
    ]

    operations = [
        migrations.RunPython(clear_manager_tools, noop),
    ]
