"""Enable the pgvector extension in PostgreSQL."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0058_fix_outlook_gradient"),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS vector;",
            reverse_sql="DROP EXTENSION IF EXISTS vector;",
        ),
    ]
