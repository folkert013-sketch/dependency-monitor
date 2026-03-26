import time

from django.core.management.base import BaseCommand
from django.db.models import Q

from dashboard.models import Prospect, ProspectGroup
from dashboard.services.geocoding import geocode_prospect


class Command(BaseCommand):
    help = "Geocode prospects die een adres hebben maar geen coordinaten."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true",
                            help="Toon welke prospects geocoded zouden worden zonder API calls.")
        parser.add_argument("--limit", type=int, default=0,
                            help="Maximaal aantal prospects om te verwerken.")
        parser.add_argument("--group", type=str, default="",
                            help="Alleen prospects in deze groep (slug).")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        group_slug = options["group"]

        qs = Prospect.objects.filter(
            Q(latitude__isnull=True) | Q(longitude__isnull=True)
        ).exclude(address="")

        if group_slug:
            group = ProspectGroup.objects.filter(slug=group_slug).first()
            if not group:
                self.stderr.write(self.style.ERROR(f"Groep '{group_slug}' niet gevonden."))
                return
            qs = qs.filter(groups=group)
            self.stdout.write(f"Filter: groep '{group.name}'")

        if limit:
            qs = qs[:limit]

        prospects = list(qs)
        total = len(prospects)

        if total == 0:
            self.stdout.write(self.style.SUCCESS("Geen prospects zonder coordinaten gevonden."))
            return

        self.stdout.write(f"{total} prospect(en) zonder coordinaten gevonden.")

        if dry_run:
            for p in prospects:
                self.stdout.write(f"  - {p.name}: {p.address[:80]}")
            self.stdout.write(self.style.WARNING(f"Dry run: {total} prospects zouden geocoded worden."))
            return

        geocoded = 0
        failed = 0
        for i, p in enumerate(prospects, 1):
            success = geocode_prospect(p)
            if success:
                geocoded += 1
                self.stdout.write(self.style.SUCCESS(
                    f"  [{i}/{total}] {p.name} -> ({p.latitude}, {p.longitude})"
                ))
            else:
                failed += 1
                self.stdout.write(self.style.WARNING(
                    f"  [{i}/{total}] {p.name} -> geen resultaat"
                ))
            time.sleep(0.1)

        self.stdout.write(self.style.SUCCESS(
            f"Klaar: {geocoded} geocoded, {failed} mislukt."
        ))
