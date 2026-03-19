from django.db import migrations, models
import django.db.models.deletion


def migrate_existing_goals(apps, schema_editor):
    """Convert existing SalesDiary goals/prospects_target to DiaryGoal records."""
    SalesDiary = apps.get_model("dashboard", "SalesDiary")
    DiaryGoal = apps.get_model("dashboard", "DiaryGoal")
    for entry in SalesDiary.objects.filter(
        models.Q(prospects_target__gt=0) | ~models.Q(goals="")
    ):
        DiaryGoal.objects.create(
            diary=entry,
            description=entry.goals,
            prospects_target=entry.prospects_target,
            prospects_contacted_actual=entry.prospects_contacted_actual,
            order=0,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0023_rename_salesdiary_prospect_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiaryGoal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(blank=True, default="", max_length=255)),
                ("prospects_target", models.IntegerField(default=0)),
                ("prospects_contacted_actual", models.IntegerField(default=0)),
                ("order", models.IntegerField(default=0)),
                ("diary", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="diary_goals", to="dashboard.salesdiary")),
            ],
            options={
                "ordering": ["order"],
            },
        ),
        migrations.RunPython(migrate_existing_goals, migrations.RunPython.noop),
    ]
