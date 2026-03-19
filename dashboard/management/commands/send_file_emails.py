import base64
import logging
import time
from pathlib import Path

from django.core.management.base import BaseCommand

from accounts.services.email_backend import send_email

logger = logging.getLogger(__name__)

TARGET_EMAIL = "documenten+3@mg.fenofin.nl"

CONTENT_TYPES = {
    ".xml": "application/xml",
    ".pdf": "application/pdf",
    ".csv": "text/csv",
    ".json": "application/json",
    ".txt": "text/plain",
}


class Command(BaseCommand):
    help = "Send each file (of a given extension) in a directory as an individual email with attachment"

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str, help="Path to the directory containing files")
        parser.add_argument("--ext", type=str, default="xml", help="File extension to look for (default: xml)")
        parser.add_argument("--exclude", type=str, default="", help="Exclude filenames containing this pattern")
        parser.add_argument("--dry-run", action="store_true", help="List files without sending emails")
        parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between emails (default: 1)")

    def handle(self, *args, **options):
        directory = Path(options["directory"])
        ext = options["ext"].lstrip(".")
        exclude = options["exclude"]
        dry_run = options["dry_run"]
        delay = options["delay"]

        if not directory.is_dir():
            self.stderr.write(self.style.ERROR(f"Directory not found: {directory}"))
            return

        files = sorted(directory.glob(f"*.{ext}"))
        if exclude:
            files = [f for f in files if exclude not in f.name]

        if not files:
            self.stderr.write(self.style.WARNING(f"No .{ext} files found in {directory}"))
            return

        content_type = CONTENT_TYPES.get(f".{ext}", "application/octet-stream")

        self.stdout.write(f"Found {len(files)} .{ext} files in {directory}")
        if exclude:
            self.stdout.write(f"Excluding filenames containing: {exclude!r}")
        self.stdout.write(f"Content-Type: {content_type}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no emails will be sent\n"))

        sent = 0
        failed = 0

        for i, file_path in enumerate(files, 1):
            filename = file_path.name
            self.stdout.write(f"[{i}/{len(files)}] {filename}", ending="")

            if dry_run:
                self.stdout.write(self.style.SUCCESS(" — would send"))
                sent += 1
                continue

            try:
                content_bytes = file_path.read_bytes()
                attachment = {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": filename,
                    "contentType": content_type,
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

                if i < len(files):
                    time.sleep(delay)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f" — FAILED: {e}"))
                logger.exception("Failed to send %s", filename)
                failed += 1

        self.stdout.write(f"\nDone: {sent} sent, {failed} failed")
