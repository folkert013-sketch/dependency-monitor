import base64
import logging
import time
from pathlib import Path

from django.core.management.base import BaseCommand

from accounts.services.email_backend import send_email

logger = logging.getLogger(__name__)

TARGET_EMAIL = "documenten+3@mg.fenofin.nl"


class Command(BaseCommand):
    help = "Send each XML file in a directory as an individual email with attachment"

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str, help="Path to the directory containing XML files")
        parser.add_argument("--dry-run", action="store_true", help="List files without sending emails")
        parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between emails (default: 1)")

    def handle(self, *args, **options):
        directory = Path(options["directory"])
        dry_run = options["dry_run"]
        delay = options["delay"]

        if not directory.is_dir():
            self.stderr.write(self.style.ERROR(f"Directory not found: {directory}"))
            return

        xml_files = sorted(directory.glob("*.xml"))
        if not xml_files:
            self.stderr.write(self.style.WARNING(f"No XML files found in {directory}"))
            return

        self.stdout.write(f"Found {len(xml_files)} XML files in {directory}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no emails will be sent\n"))

        sent = 0
        failed = 0

        for i, xml_path in enumerate(xml_files, 1):
            filename = xml_path.name
            self.stdout.write(f"[{i}/{len(xml_files)}] {filename}", ending="")

            if dry_run:
                self.stdout.write(self.style.SUCCESS(" — would send"))
                sent += 1
                continue

            try:
                content_bytes = xml_path.read_bytes()
                attachment = {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": filename,
                    "contentType": "application/xml",
                    "contentBytes": base64.b64encode(content_bytes).decode("ascii"),
                }

                send_email(
                    to=TARGET_EMAIL,
                    subject=filename,
                    plain_body=f"Bijlage: {filename}",
                    html_body=f"<p>Bijlage: {filename}</p>",
                    attachments=[attachment],
                )

                self.stdout.write(self.style.SUCCESS(" — sent"))
                sent += 1

                if i < len(xml_files):
                    time.sleep(delay)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f" — FAILED: {e}"))
                logger.exception("Failed to send %s", filename)
                failed += 1

        self.stdout.write(f"\nDone: {sent} sent, {failed} failed")
