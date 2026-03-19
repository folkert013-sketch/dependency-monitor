from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0027_remove_prospect_contact_person_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='responsetemplate',
            name='is_starred',
            field=models.BooleanField(default=False),
        ),
    ]
