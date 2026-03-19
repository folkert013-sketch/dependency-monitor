from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0022_fix_prospect_place_id_constraint"),
    ]

    operations = [
        migrations.RenameField(
            model_name="salesdiary",
            old_name="prospects_contacted",
            new_name="prospects_target",
        ),
        migrations.RenameField(
            model_name="salesdiary",
            old_name="prospects_interested",
            new_name="prospects_contacted_actual",
        ),
    ]
