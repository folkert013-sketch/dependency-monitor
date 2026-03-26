"""Add background-color fallback for Outlook which doesn't support linear-gradient."""

from django.db import migrations


def fix_gradient(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    for tpl in ResponseTemplate.objects.filter(slug__in=["bouwbedrijven", "klant-zzp-dga"]):
        if tpl.html_template and "background:linear-gradient(" in tpl.html_template:
            tpl.html_template = tpl.html_template.replace(
                "background:linear-gradient(",
                "background-color:#4f46e5;background-image:linear-gradient(",
            )
            tpl.save(update_fields=["html_template"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0057_add_indexes_and_constraints"),
    ]

    operations = [
        migrations.RunPython(fix_gradient, noop),
    ]
