import json
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Finding, Report
from monitor.run import run_crew


class Command(BaseCommand):
    help = "Run the CrewAI dependency monitor crew and save results to the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--requirements",
            type=str,
            default="",
            help="Path to requirements.txt (default: from settings/env)",
        )

    def handle(self, *args, **options):
        requirements_path = options["requirements"]
        if not requirements_path:
            from pathlib import Path
            requirements_path = str(Path(settings.MONITORED_PROJECT_PATH) / "requirements.txt")

        self.stdout.write(f"Starting dependency monitor scan...")
        self.stdout.write(f"Requirements: {requirements_path}")

        try:
            results = run_crew(requirements_path)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Crew failed: {e}"))
            traceback.print_exc()
            # Save error report
            Report.objects.create(
                status="critical",
                action_required=True,
                raw_output={"error": str(e), "traceback": traceback.format_exc()},
            )
            return

        # Create Report
        report = Report.objects.create(
            status=results["status"],
            total_dependencies=results["total_dependencies"],
            outdated_count=results["outdated_count"],
            vulnerability_count=results["vulnerability_count"],
            action_required=results["status"] in ("critical", "warning"),
            tip_of_the_week=results["tip_of_the_week"],
            quote_of_the_week=results["quote_of_the_week"],
            total_tokens=results["total_tokens"],
            estimated_cost=results["estimated_cost"],
            raw_output={
                "raw": results["raw_output"][:50000],  # Limit stored size
                "findings_count": len(results["findings"]),
            },
        )

        # Create Findings
        for finding_data in results["findings"]:
            Finding.objects.create(
                report=report,
                severity=finding_data.get("severity", "info"),
                category=finding_data.get("category", "outdated"),
                package_name=finding_data.get("package_name", "Unknown"),
                current_version=finding_data.get("current_version", ""),
                latest_version=finding_data.get("latest_version", ""),
                summary=finding_data.get("summary", ""),
                action_steps=finding_data.get("action_steps", ""),
            )

        status_style = {
            "critical": self.style.ERROR,
            "warning": self.style.WARNING,
            "ok": self.style.SUCCESS,
        }
        style_fn = status_style.get(results["status"], self.style.SUCCESS)

        self.stdout.write(style_fn(
            f"\nReport saved (ID: {report.pk})\n"
            f"Status: {report.get_status_display()}\n"
            f"Dependencies: {report.total_dependencies}\n"
            f"Vulnerabilities: {report.vulnerability_count}\n"
            f"Findings: {report.findings.count()}\n"
            f"Tokens: {report.total_tokens}\n"
            f"Cost: ${report.estimated_cost}"
        ))
