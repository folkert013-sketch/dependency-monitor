"""Seed APIUsageLog with historical data from Report and BlogArticle."""

from django.db import migrations


def forward(apps, schema_editor):
    APIUsageLog = apps.get_model("dashboard", "APIUsageLog")
    Report = apps.get_model("dashboard", "Report")
    BlogArticle = apps.get_model("dashboard", "BlogArticle")

    logs = []
    for r in Report.objects.filter(total_tokens__gt=0):
        logs.append(APIUsageLog(
            service="gemini",
            description="Dependency Monitor scan (historisch)",
            total_tokens=r.total_tokens,
            estimated_cost=r.estimated_cost,
            api_calls=1,
            created_at=r.created_at,
        ))
    for a in BlogArticle.objects.filter(total_tokens__gt=0):
        logs.append(APIUsageLog(
            service="gemini",
            description=f"Fiscaal artikel: {a.title[:200]} (historisch)",
            total_tokens=a.total_tokens,
            estimated_cost=a.estimated_cost,
            api_calls=1,
            created_at=a.created_at,
        ))
    if logs:
        APIUsageLog.objects.bulk_create(logs)


def backward(apps, schema_editor):
    APIUsageLog = apps.get_model("dashboard", "APIUsageLog")
    APIUsageLog.objects.filter(description__endswith="(historisch)").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0047_add_api_usage_log"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
