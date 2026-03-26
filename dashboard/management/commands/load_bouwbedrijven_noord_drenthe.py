"""
Management command: laad 9 bouwbedrijven uit Noord-Drenthe/Groningen als prospects.

Usage:
    python manage.py load_bouwbedrijven_noord_drenthe
"""

from django.core.management.base import BaseCommand

from dashboard.models import Prospect, ProspectGroup

BOUWBEDRIJVEN = [
    {
        "name": "AABS Bouw- en Timmerbedrijf",
        "address": "Meerweg 12, 9482 TE Tynaarlo",
        "website": "aabsbouw.nl",
        "email": "info@aabsbouw.nl",
        "phone": "0592-544840",
        "contact_first_name": "Jan Jaap",
        "contact_last_name": "Boersma",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: fietsafstand (~5 min)\n"
            "Rechtsvorm: BV (via B-Solid Bouw BV)\n"
            "KvK: 69763356 (VOF) / 04053048 (BV)\n"
            "Specialisatie: Nieuwbouw, verbouw, renovatie\n"
            "Opmerking: Per 1 sept 2023 overgenomen door B-Solid Bouw BV (Jan Jaap Boersma)"
        ),
    },
    {
        "name": "Bouwbedrijf Doornbos",
        "address": "Energieweg 7-9, 9482 WH Tynaarlo",
        "website": "bouwbedrijfdoornbos.nl",
        "email": "info@doorbouw.nl",
        "phone": "0592-542400",
        "contact_first_name": "Edward",
        "contact_last_name": "Doornbos",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: fietsafstand (~5 min)\n"
            "Rechtsvorm: BV (KvK 70392587)\n"
            "Opgericht: 2012 (doorstart)\n"
            "Specialisatie: Nieuwbouw, verbouw\n"
            "Opmerking: Investeert al in WKB-software — sterk digitaliseringssignaal"
        ),
    },
    {
        "name": "Van Delden Bouw",
        "address": "Dorpsstraat 172, 9605 PE Kiel-Windeweer",
        "website": "vandeldenbouw.nl",
        "email": "",
        "phone": "0598-491888",
        "contact_first_name": "Hans",
        "contact_last_name": "van Delden",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: 15 min rijden\n"
            "Rechtsvorm: BV (KvK 02093337)\n"
            "Medewerkers: ~20\n"
            "Opgericht: 1805 — 7e-generatie familiebedrijf\n"
            "Specialisatie: ISO/VCA-pionier\n"
            "Opmerking: Hans van Delden nam in 2023 over van vader Martin (6e gen.) "
            "— generatieoverdracht = ideaal moment voor software-evaluatie\n"
            "E-mail niet publiek beschikbaar (alleen contactformulier op website)"
        ),
    },
    {
        "name": "Bouwbedrijf Rotteveel",
        "address": "Broeklaan 22, 9405 AM Assen",
        "website": "bouwbedrijfrotteveel.nl",
        "email": "info@bouwbedrijfrotteveel.nl",
        "phone": "0592-355278",
        "contact_first_name": "Johan",
        "contact_last_name": "Bijl",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: 15 min rijden\n"
            "Rechtsvorm: BV (KvK 04010762)\n"
            "Medewerkers: ~26\n"
            "Omzet: €4 mln\n"
            "Opgericht: 1919 — 100+ jaar oud\n"
            "Reviews: 4.6★"
        ),
    },
    {
        "name": "HTO Aannemingsbedrijf",
        "address": "Van Heekstraat 7, 9403 AT Assen",
        "website": "hto.nl",
        "email": "info@hto.nl",
        "phone": "0592-343641",
        "contact_first_name": "Herman",
        "contact_last_name": "Manning",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: 15 min rijden\n"
            "Rechtsvorm: BV (KvK 04037565, moeder: MTF Beheer BV)\n"
            "Medewerkers: ~30\n"
            "Voluit: Huisman van Triest Offringa\n"
            "Specialisatie: breed portfolio (zorg, woningcorporaties, GWW)"
        ),
    },
    {
        "name": "Geveke Bouw",
        "address": "Machlaan 35, 9761 TK Eelde",
        "website": "gevekebouw.nl",
        "email": "info@gevekebouw.nl",
        "phone": "050-5334777",
        "contact_first_name": "Martijn",
        "contact_last_name": "Gils",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: 15 min rijden\n"
            "Rechtsvorm: BV (KvK 02041666)\n"
            "Medewerkers: ~138\n"
            "Opgericht: 1986\n"
            "Specialisatie: utiliteitsbouw & gebiedsontwikkeling\n"
            "Opmerking: Martijn Gils werd alg. directeur/eigenaar in jan 2022"
        ),
    },
    {
        "name": "IBV Venema Installatietechniek",
        "address": "De Overzet 2-2B, 9321 DB Peize",
        "website": "ibvvenema.nl",
        "email": "info@ibv-venema.nl",
        "phone": "050-5032576",
        "contact_first_name": "Frits",
        "contact_last_name": "Smilda",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: 25 min rijden\n"
            "Rechtsvorm: BV (KvK 01131869)\n"
            "Medewerkers: ~40\n"
            "Opgericht: 1990\n"
            "Specialisatie: installatietechniek, 2.000 onderhoudscontracten\n"
            "Opmerking: Veel data = veel analyse-potentieel. "
            "Frits Smilda nam over van oprichter Bert Venema. "
            "Vestigingen in Peize en Leek"
        ),
    },
    {
        "name": "Bouwbedrijf De Boer",
        "address": "Wismarweg 23, 9723 HC Groningen",
        "website": "bouwbedrijf-deboer.nl",
        "email": "info@bouwbedrijf-deboer.nl",
        "phone": "050-5472100",
        "contact_first_name": "Klaas",
        "contact_last_name": "de Boer",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: 25 min rijden\n"
            "Rechtsvorm: BV (KvK 02074595)\n"
            "Medewerkers: ~25\n"
            "Opgericht: 2001\n"
            "Specialisatie: woningbouw + aardbevingsschadeherstel\n"
            "Opmerking: Directie samen met Marijke de Boer-Ellerie"
        ),
    },
    {
        "name": "Dekker Struik Installatietechniek",
        "address": "Bremenweg 10, 9723 TD Groningen",
        "website": "dekkerstruikinstallatietechniek.nl",
        "email": "info@dekkerstruikinstallatietechniek.nl",
        "phone": "050-3135151",
        "contact_first_name": "Jan Willem",
        "contact_last_name": "Siepelinga",
        "aanhef": "Geachte heer",
        "notes": (
            "Afstand: 25 min rijden\n"
            "Rechtsvorm: BV (KvK 02026229)\n"
            "Medewerkers: 10-20\n"
            "Opgericht: 1960 (fusie 2008: Dekker + Struik)\n"
            "Specialisatie: elektro, klimaat, duurzame energie\n"
            "Opmerking: Sinds okt 2024 onderdeel van Kon. Damstra Installatiegroep. "
            "Jan Willem Siepelinga is vestigingsleider. "
            "Voormalige eigenaren Ferry Dekker en John Struik zijn nu projectleiders. "
            "Vestigingen in Groningen en Assen"
        ),
    },
]


class Command(BaseCommand):
    help = "Laad 9 bouwbedrijven uit Noord-Drenthe/Groningen als prospects"

    def handle(self, *args, **options):
        group, created = ProspectGroup.objects.get_or_create(
            slug="bouwbedrijven-noord-drenthe",
            defaults={
                "name": "Bouwbedrijven Noord-Drenthe",
                "description": "Bouwbedrijven en installatiebedrijven in de regio Noord-Drenthe/Groningen",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Groep aangemaakt: {group.name}"))
        else:
            self.stdout.write(f"Groep bestaat al: {group.name}")

        created_count = 0
        skipped_count = 0

        for data in BOUWBEDRIJVEN:
            existing = Prospect.objects.filter(name=data["name"]).first()
            if existing:
                if not existing.groups.filter(pk=group.pk).exists():
                    existing.groups.add(group)
                skipped_count += 1
                self.stdout.write(f"  ~ {existing.name} (bestaat al)")
            else:
                prospect = Prospect(
                    name=data["name"],
                    address=data["address"],
                    website=data["website"],
                    email=data["email"],
                    phone=data["phone"],
                    contact_first_name=data["contact_first_name"],
                    contact_last_name=data["contact_last_name"],
                    aanhef=data["aanhef"],
                    business_type="Bouwbedrijf",
                    status="new",
                    notes=data["notes"],
                )
                prospect.save()
                prospect.groups.add(group)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  + {prospect.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nKlaar: {created_count} aangemaakt, {skipped_count} overgeslagen"
            )
        )
