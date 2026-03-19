from django.db import migrations


def seed_business_types(apps, schema_editor):
    BusinessType = apps.get_model("dashboard", "BusinessType")
    defaults = [
        ("accounting", "Administratiekantoor"),
        ("tax_preparation_service", "Belastingadviseur"),
        ("financial_planner", "Financieel adviseur"),
        ("insurance_agency", "Verzekeringsadviseur"),
        ("lawyer", "Advocaat"),
    ]
    for google_type, label in defaults:
        BusinessType.objects.get_or_create(google_type=google_type, defaults={"label": label})


def unseed_business_types(apps, schema_editor):
    BusinessType = apps.get_model("dashboard", "BusinessType")
    BusinessType.objects.filter(
        google_type__in=["accounting", "tax_preparation_service", "financial_planner", "insurance_agency", "lawyer"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0017_add_not_contacted_status_and_business_type"),
    ]

    operations = [
        migrations.RunPython(seed_business_types, unseed_business_types),
    ]
