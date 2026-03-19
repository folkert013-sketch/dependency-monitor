from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0029_prospect_aanhef_prospect_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="responsetemplate",
            name="html_template",
            field=models.TextField(blank=True, default=""),
        ),
    ]
