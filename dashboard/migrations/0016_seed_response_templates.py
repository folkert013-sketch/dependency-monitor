from django.db import migrations


def seed_templates(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    templates = [
        {
            "name": "Particulieren",
            "slug": "particulieren",
            "category": "particulier",
            "order": 1,
            "body": (
                "Beste heer/mevrouw,\n\n"
                "Wij zijn FenoFin, een administratiekantoor dat zich richt op particulieren "
                "die op zoek zijn naar persoonlijke begeleiding bij hun belastingaangifte en "
                "financiële administratie.\n\n"
                "Graag maken wij kennis met u om te bespreken hoe wij u kunnen ontzorgen.\n\n"
                "Met vriendelijke groet,\n"
                "FenoFin"
            ),
        },
        {
            "name": "Administratiekantoren",
            "slug": "administratiekantoren",
            "category": "kantoor",
            "order": 2,
            "body": (
                "Beste collega,\n\n"
                "Wij zijn FenoFin en wij zijn geïnteresseerd in een mogelijke samenwerking. "
                "Als administratiekantoor zien wij kansen om kennis en diensten te delen.\n\n"
                "Zouden wij een keer vrijblijvend kennis kunnen maken?\n\n"
                "Met vriendelijke groet,\n"
                "FenoFin"
            ),
        },
    ]
    for tpl in templates:
        ResponseTemplate.objects.get_or_create(slug=tpl["slug"], defaults=tpl)


def remove_templates(apps, schema_editor):
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")
    ResponseTemplate.objects.filter(slug__in=["particulieren", "administratiekantoren"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0015_responsetemplate_prospectresponse"),
    ]

    operations = [
        migrations.RunPython(seed_templates, remove_templates),
    ]
