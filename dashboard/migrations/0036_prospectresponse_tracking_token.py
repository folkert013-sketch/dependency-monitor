import uuid

from django.db import migrations, models


def populate_tracking_tokens(apps, schema_editor):
    """Generate unique UUIDs for existing ProspectResponse rows."""
    ProspectResponse = apps.get_model("dashboard", "ProspectResponse")
    for pr in ProspectResponse.objects.all():
        pr.tracking_token = uuid.uuid4()
        pr.save(update_fields=["tracking_token"])


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0035_website_urlfield_to_charfield"),
    ]

    operations = [
        # Step 1: Add nullable, non-unique field
        migrations.AddField(
            model_name="prospectresponse",
            name="tracking_token",
            field=models.UUIDField(default=uuid.uuid4, null=True, editable=False),
        ),
        # Step 2: Populate existing rows with unique UUIDs
        migrations.RunPython(populate_tracking_tokens, migrations.RunPython.noop),
        # Step 3: Make non-nullable and unique
        migrations.AlterField(
            model_name="prospectresponse",
            name="tracking_token",
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
    ]
