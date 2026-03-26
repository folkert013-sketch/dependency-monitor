"""
Management command: laad 14 administratiekantoren uit Noord-Nederland als prospects.

Usage:
    python manage.py load_noord_nederland_kantoren
"""

from django.core.management.base import BaseCommand

from dashboard.models import Prospect, ProspectGroup

KANTOREN = [
    {
        "name": "Trippel AAA / Triacc",
        "address": "Stadskanaal, Emmen, Hoogezand, Meppel, Klazienaveen, Schoonebeek",
        "website": "trippelaaa.nl / triacc.nl",
        "email": "info@trippelaaa.nl",
        "phone": "0599-696490",
        "notes": (
            "Provincie: GR/DR\n"
            "Medewerkers: ~70\n"
            "Omzet: €3,97 mln (2023)\n"
            "Klanten: n.b.\n"
            "NOAB: Ja\n"
            "Specialisatie: Agrarisch, MKB"
        ),
    },
    {
        "name": "Apuls Cijfers & Advies",
        "address": "Burgum",
        "website": "apuls.nl",
        "email": "info@apuls.nl",
        "phone": "0511-462075",
        "notes": (
            "Provincie: FR\n"
            "Medewerkers: ~20\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Niet bevestigd\n"
            "Specialisatie: Fiscaal, financieel, HRM, subsidies"
        ),
    },
    {
        "name": "Deelstra Jansen",
        "address": "Archimedesweg 5, Leeuwarden",
        "website": "deelstrajansen.nl",
        "email": "info@deelstrajansen.nl",
        "phone": "0888-181818",
        "notes": (
            "Provincie: FR\n"
            "Medewerkers: 16\n"
            "Omzet: n.b.\n"
            "Klanten: ~300\n"
            "NOAB: Ja\n"
            "Specialisatie: Agrarisch (50%), MKB (50%)\n"
            "Opmerking: Verhuisd van Grou naar Leeuwarden"
        ),
    },
    {
        "name": "Tribus Financial Services",
        "address": "Mediacentrale, Groningen",
        "website": "tribus-financialservices.nl",
        "email": "info@tribus-financialservices.nl",
        "phone": "050-2053039",
        "notes": (
            "Provincie: GR\n"
            "Medewerkers: 14-16\n"
            "Omzet: n.b.\n"
            "Klanten: ~400\n"
            "NOAB: Nee\n"
            "Specialisatie: Scale-ups, BV's, CFO-as-a-service"
        ),
    },
    {
        "name": "Administratiekantoor S. de Jong",
        "address": "Heerenveen",
        "website": "kantoordejong.frl",
        "email": "info@kantoordejong.nl",
        "phone": "0513-653222",
        "notes": (
            "Provincie: FR\n"
            "Medewerkers: 11\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Niet bevestigd\n"
            "Specialisatie: Breed, cloud-boekhouding\n"
            "Opmerking: Sinds 2025 onderdeel van Join Administraties"
        ),
    },
    {
        "name": "Adm.kantoor Woldendorp",
        "address": "Bedum (Het Hogeland)",
        "website": "woldendorp.net",
        "email": "info@woldendorp.net",
        "phone": "050-3012819",
        "notes": (
            "Provincie: GR\n"
            "Medewerkers: 10-19\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Nee (VABnet)\n"
            "Specialisatie: Agrarisch, MKB"
        ),
    },
    {
        "name": "Kuipers Administratie & Advies",
        "address": "Groningen",
        "website": "kuipersadviseurs.nl",
        "email": "algemeen@kuipersadviseurs.nl",
        "phone": "050-5258338",
        "notes": (
            "Provincie: GR\n"
            "Medewerkers: ~10\n"
            "Omzet: n.b.\n"
            "Klanten: Honderden\n"
            "NOAB: Ja\n"
            "Specialisatie: MKB, breed softwareportfolio"
        ),
    },
    {
        "name": "Stevens & Partners",
        "address": "Beilen",
        "website": "stevensenpartners.nl",
        "email": "info@stevensenpartners.nl",
        "phone": "0593-525253",
        "notes": (
            "Provincie: DR\n"
            "Medewerkers: 9\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Niet bevestigd\n"
            "Specialisatie: Administratie, online boekhouden"
        ),
    },
    {
        "name": "Adm.kantoor F. Hanken",
        "address": "Schoonebeek",
        "website": "administratiekantoorhanken.nl",
        "email": "info@adm-hanken.nl",
        "phone": "0524-532934",
        "notes": (
            "Provincie: DR\n"
            "Medewerkers: 9\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Nee\n"
            "Specialisatie: Agrarisch, MKB\n"
            "Opmerking: Nu bij Trippel AAA"
        ),
    },
    {
        "name": "Administratiekantoor Assen",
        "address": "Overcingellaan 17, Assen",
        "website": "administratiekantoor-assen.nl",
        "email": "info@administratiekantoor-assen.nl",
        "phone": "0592-201256",
        "notes": (
            "Provincie: DR\n"
            "Medewerkers: 7\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Nee\n"
            "Specialisatie: Breed, lage tarieven"
        ),
    },
    {
        "name": "Adm.kantoor Groningen (Mediolead)",
        "address": "Bieslookstraat 31, Groningen",
        "website": "mediolead.nl",
        "email": "info@mediolead.nl",
        "phone": "050-5778651",
        "notes": (
            "Provincie: GR\n"
            "Medewerkers: 7\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Nee\n"
            "Specialisatie: ZZP, MKB, loonadministratie"
        ),
    },
    {
        "name": "Kroezen & Sieders",
        "address": "Elbe 6, Hoogeveen",
        "website": "kroezen-sieders.nl",
        "email": "info@kroezen-sieders.nl",
        "phone": "0528-267858",
        "notes": (
            "Provincie: DR\n"
            "Medewerkers: 6-15\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Ja\n"
            "Specialisatie: MKB, starters, breed Drenthe"
        ),
    },
    {
        "name": "CSB Breukers",
        "address": "Donau 1-31, Hoogeveen",
        "website": "csbbreukers.nl",
        "email": "",
        "phone": "0528-266215",
        "notes": (
            "Provincie: DR\n"
            "Medewerkers: 5-9\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: Nee\n"
            "Specialisatie: MKB\n"
            "Opmerking: E-mail niet publiek gevonden (alleen contactformulier)"
        ),
    },
    {
        "name": "Findi",
        "address": "James Wattstraat 6, Franeker",
        "website": "findi.nl",
        "email": "info@findi.nl",
        "phone": "0517-235231",
        "notes": (
            "Provincie: FR\n"
            "Medewerkers: n.b.\n"
            "Omzet: n.b.\n"
            "Klanten: n.b.\n"
            "NOAB: n.b.\n"
            "Specialisatie: n.b."
        ),
    },
]


class Command(BaseCommand):
    help = "Laad 14 administratiekantoren uit Noord-Nederland als prospects"

    def handle(self, *args, **options):
        group, created = ProspectGroup.objects.get_or_create(
            slug="administratiekantoren-noord-nederland",
            defaults={
                "name": "Administratiekantoren Noord-Nederland",
                "description": "Administratiekantoren in Groningen, Drenthe en Friesland",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Groep aangemaakt: {group.name}"))
        else:
            self.stdout.write(f"Groep bestaat al: {group.name}")

        created_count = 0
        skipped_count = 0

        for data in KANTOREN:
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
                    business_type="Administratiekantoor",
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
