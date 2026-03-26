"""Seed LinkedIn outreach templates with 'LinkedIn' category."""

from django.db import migrations

TEMPLATES = [
    {
        "name": "LinkedIn \u2014 Introductie",
        "slug": "linkedin-introductie",
        "subject": "",
        "order": 0,
        "body": (
            "Ik ben Folkert Feenstra, AA-accountant met ICT-affiniteit. "
            "Ik ondersteun MKB-bedrijven in de bouw en techniek met "
            "administratie en ICT \u2014 als extern aanspreekpunt. "
            "Interesse in een gesprek? Folkert | FenoFin B.V."
        ),
    },
    {
        "name": "LinkedIn \u2014 Vraag",
        "slug": "linkedin-vraag",
        "subject": "",
        "order": 1,
        "body": (
            "Wie regelt bij uw bedrijf de boekhouding en ICT? "
            "Als AA-accountant met ICT-achtergrond bied ik "
            "\u00e9\u00e9n aanspreekpunt voor beide \u2014 flexibel "
            "en voordelig. Open voor een gesprek? "
            "Folkert Feenstra | FenoFin B.V."
        ),
    },
    {
        "name": "LinkedIn \u2014 Connectie",
        "slug": "linkedin-connectie",
        "subject": "",
        "order": 2,
        "body": (
            "Graag verbind ik met u. Ik ben Folkert Feenstra, "
            "AA-accountant met affiniteit voor ICT. Ik help bouw- en "
            "techniekbedrijven met administratie en IT-beheer. "
            "Folkert | FenoFin B.V."
        ),
    },
    {
        "name": "LinkedIn \u2014 Netwerker",
        "slug": "linkedin-netwerker",
        "subject": "",
        "order": 3,
        "body": (
            "Graag voeg ik u toe aan mijn netwerk. Als AA-accountant "
            "met een focus op IT-automatisering in de bouw, volg ik "
            "graag wat er speelt bij bedrijven in deze sector. Wellicht "
            "kunnen we in de toekomst iets voor elkaar betekenen. "
            "Groet, Folkert"
        ),
    },
]


def seed_linkedin_templates(apps, schema_editor):
    TemplateCategory = apps.get_model("dashboard", "TemplateCategory")
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    category, _ = TemplateCategory.objects.get_or_create(
        slug="linkedin",
        defaults={"name": "LinkedIn", "color": "sky", "order": 10},
    )

    for data in TEMPLATES:
        ResponseTemplate.objects.update_or_create(
            slug=data["slug"],
            defaults={
                "name": data["name"],
                "subject": data["subject"],
                "body": data["body"],
                "html_template": "",
                "is_starred": False,
                "category": category,
                "order": data["order"],
            },
        )


def remove_linkedin_templates(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    TemplateCategory = apps.get_model("dashboard", "TemplateCategory")

    ResponseTemplate.objects.filter(
        slug__in=[t["slug"] for t in TEMPLATES]
    ).delete()
    TemplateCategory.objects.filter(slug="linkedin").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0069_update_kort_automatisering_signatures"),
    ]

    operations = [
        migrations.RunPython(seed_linkedin_templates, remove_linkedin_templates),
    ]
