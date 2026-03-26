"""Seed ProspectGroups for vacancy scraping categories."""

from django.db import migrations


def seed_groups(apps, schema_editor):
    ProspectGroup = apps.get_model("dashboard", "ProspectGroup")
    groups = [
        {
            "name": "Vacatures - Financieel Administratie",
            "slug": "vacatures-financieel-administratie",
            "description": "Bedrijven met vacatures voor financieel administratie in Noord-Nederland",
        },
        {
            "name": "Vacatures - Data-analyse",
            "slug": "vacatures-data-analyse",
            "description": "Bedrijven met vacatures voor data-analyse in Noord-Nederland",
        },
        {
            "name": "Vacatures - ICT en Netwerken",
            "slug": "vacatures-ict-en-netwerken",
            "description": "Bedrijven met vacatures voor ICT en netwerken in Noord-Nederland",
        },
    ]
    for g in groups:
        ProspectGroup.objects.get_or_create(slug=g["slug"], defaults=g)


def reverse(apps, schema_editor):
    ProspectGroup = apps.get_model("dashboard", "ProspectGroup")
    ProspectGroup.objects.filter(
        slug__in=[
            "vacatures-financieel-administratie",
            "vacatures-data-analyse",
            "vacatures-ict-en-netwerken",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0044_add_vacancy_model"),
    ]

    operations = [
        migrations.RunPython(seed_groups, reverse),
    ]
