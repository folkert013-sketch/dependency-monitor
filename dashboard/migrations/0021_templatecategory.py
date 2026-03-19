from django.db import migrations, models
import django.db.models.deletion


def seed_categories_and_link(apps, schema_editor):
    TemplateCategory = apps.get_model("dashboard", "TemplateCategory")
    ResponseTemplate = apps.get_model("dashboard", "ResponseTemplate")

    cat_particulier = TemplateCategory.objects.create(
        name="Particulier", slug="particulier", color="blue", order=0,
    )
    cat_kantoor = TemplateCategory.objects.create(
        name="Administratiekantoor", slug="administratiekantoor", color="purple", order=1,
    )

    mapping = {
        "particulier": cat_particulier,
        "kantoor": cat_kantoor,
    }
    for tpl in ResponseTemplate.objects.all():
        old_val = tpl.old_category or ""
        tpl.category = mapping.get(old_val)
        tpl.save(update_fields=["category"])


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0020_fix_prospect_response_sent_at"),
    ]

    operations = [
        # 1. Create TemplateCategory model
        migrations.CreateModel(
            name="TemplateCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("color", models.CharField(
                    choices=[("blue", "Blauw"), ("indigo", "Indigo"), ("purple", "Paars"),
                             ("emerald", "Groen"), ("amber", "Oranje"), ("rose", "Roze"),
                             ("teal", "Teal"), ("sky", "Lichtblauw")],
                    default="indigo", max_length=10,
                )),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["order", "name"]},
        ),
        # 2. Rename old category CharField so we can reuse the name
        migrations.RenameField(
            model_name="responsetemplate",
            old_name="category",
            new_name="old_category",
        ),
        # 3. Add new FK category field
        migrations.AddField(
            model_name="responsetemplate",
            name="category",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="templates",
                to="dashboard.templatecategory",
            ),
        ),
        # 4. Seed categories and link existing templates
        migrations.RunPython(seed_categories_and_link, migrations.RunPython.noop),
        # 5. Remove old CharField
        migrations.RemoveField(
            model_name="responsetemplate",
            name="old_category",
        ),
    ]
