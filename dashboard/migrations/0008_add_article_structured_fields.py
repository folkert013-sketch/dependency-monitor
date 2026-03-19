from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0007_seed_builtin_teams"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogarticle",
            name="key_takeaways",
            field=models.JSONField(blank=True, default=list, help_text="Kernpunten van het artikel"),
        ),
        migrations.AddField(
            model_name="blogarticle",
            name="action_items",
            field=models.JSONField(blank=True, default=list, help_text="Concrete actiepunten voor de ondernemer"),
        ),
        migrations.AddField(
            model_name="blogarticle",
            name="deadline_date",
            field=models.DateField(blank=True, help_text="Relevante deadline datum", null=True),
        ),
        migrations.AddField(
            model_name="blogarticle",
            name="relevance_tags",
            field=models.JSONField(blank=True, default=list, help_text="Doelgroep tags (mkb, zzp, bv, etc.)"),
        ),
    ]
