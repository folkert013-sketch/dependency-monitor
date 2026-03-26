"""
Parse 'Wegwijs in de Vennootschapsbelasting' markdown naar database.

Werkt op een eerder gegenereerd .md bestand (via ocr_pdf_to_markdown command).
"""

import os
import re

from django.core.management.base import BaseCommand

from dashboard.models import VpbBoekHoofdstuk, VpbBoekPassage, VpbBoekSectie

# Regex patronen voor boekstructuur
# Hoofdstukken: "# 1 De vennootschapsbelasting..." of "# 2 ..."
RE_HOOFDSTUK = re.compile(r"^#\s+(\d+)\s+(.+)$")
# Secties: "## 1.1 Inleiding", "### 1.1.1 Titel", "## 2B.3.3 Art. 2..."
# Let op: het boek gebruikt codes als "2B.3.3", "8B.4.4.4" met letters
RE_SECTIE = re.compile(r"^#{2,3}\s+(\d+[A-Z]?\.\d+(?:\.\d+)*)\s+(.+)$")
# Deel-koppen: "## Deel A / Titel" of "## Deel B / Titel / pagina"
RE_DEEL = re.compile(r"^##\s+Deel\s+([A-Z])\s*/\s*(.+?)(?:\s*/\s*\d+)?$")
RE_PAGINA = re.compile(r"^---\s*Pagina\s+(\d+)\s*---$")

# Bekende hoofdstukken en hun titels (voor detectie via sectienummering)
KNOWN_CHAPTERS = {
    "1": "De vennootschapsbelasting in Nederland en Europa",
    "2": "De subjectieve belastingplicht",
    "3": "De algemene regels van de winstbepaling bij binnenlandse belastingplichtigen",
    "4": "Renteaftrekbeperkingen en de regeling tegen hybride mismatches",
    "5": "De deelnemingsvrijstelling",
    "6": "De bedrijfsfusie, juridische splitsing, juridische fusie en omzetting",
    "7": "De bedrijfsopvolgingsregeling",
    "8": "De fiscale eenheid",
    "9": "De eindafrekening en objectvrijstelling",
    "10": "Verliesverrekening",
    "11": "Giftenaftrek",
    "12": "De innovatiebox",
    "13": "Het VPB-tarief",
    "14": "Aanslag, voorheffingen en aansprakelijkheid",
    "15": "De buitenlandse belastingplicht",
    "16": "De verzekeringsondernemingen",
}

# Maximale passage-lengte (in woorden)
MAX_PASSAGE_WORDS = 800
OVERLAP_WORDS = 100


class Command(BaseCommand):
    help = "Parse VPB boek markdown naar database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            help="Pad naar het markdown-bestand",
        )
        parser.add_argument(
            "--editie",
            default="2023",
            help="Editie/boekjaar (default: 2023), bijv. 2025",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Verwijder bestaande boekdata voor deze editie",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        clear = options["clear"]
        self._editie = options.get("editie", "2023")

        if not os.path.isfile(file_path):
            self.stderr.write(self.style.ERROR(f"Bestand niet gevonden: {file_path}"))
            return

        if clear:
            self.stdout.write(f"Bestaande boekdata verwijderen voor editie {self._editie}...")
            hst_ids = VpbBoekHoofdstuk.objects.filter(editie=self._editie).values_list("pk", flat=True)
            VpbBoekPassage.objects.filter(sectie__hoofdstuk__pk__in=hst_ids).delete()
            VpbBoekSectie.objects.filter(hoofdstuk__pk__in=hst_ids).delete()
            VpbBoekHoofdstuk.objects.filter(editie=self._editie).delete()

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.stdout.write(f"Bestand geladen: {len(content)} tekens")

        self._parse_content(content)

        self.stdout.write(self.style.SUCCESS(
            f"Klaar: "
            f"{VpbBoekHoofdstuk.objects.count()} hoofdstukken, "
            f"{VpbBoekSectie.objects.count()} secties, "
            f"{VpbBoekPassage.objects.count()} passages"
        ))

    def _get_or_create_chapter(self, nummer, titel=None):
        """Haal een hoofdstuk op of maak het aan."""
        if titel is None:
            titel = KNOWN_CHAPTERS.get(nummer, f"Hoofdstuk {nummer}")
        obj, created = VpbBoekHoofdstuk.objects.update_or_create(
            nummer=nummer,
            editie=self._editie,
            defaults={"titel": titel, "order": int(nummer) if nummer.isdigit() else 0},
        )
        if created:
            self.stdout.write(f"  Hoofdstuk {nummer}: {titel}")
        return obj

    def _chapter_from_section_code(self, code):
        """Extraheer hoofdstuknummer uit sectiecode (bijv. '2B.3.3' -> '2', '8B.4' -> '8')."""
        m = re.match(r"(\d+)", code)
        return m.group(1) if m else None

    def _parse_content(self, content):
        """Parse de markdown content naar DB records."""
        lines = content.split("\n")

        current_hoofdstuk = None
        current_sectie = None
        current_page = None
        current_text = []
        sectie_order = 0
        passage_order = 0

        for line in lines:
            # Check paginanummer
            page_match = RE_PAGINA.match(line)
            if page_match:
                current_page = int(page_match.group(1))
                continue

            # Check hoofdstuk: "# 3 De algemene regels..."
            hoofdstuk_match = RE_HOOFDSTUK.match(line)
            if hoofdstuk_match:
                # Flush
                if current_text and current_sectie:
                    passage_order = self._save_passages(
                        current_sectie, current_text, current_page, passage_order
                    )
                    current_text = []

                nummer = hoofdstuk_match.group(1)
                titel = hoofdstuk_match.group(2).strip()
                current_hoofdstuk = self._get_or_create_chapter(nummer, titel)
                sectie_order = 1
                passage_order = 0
                current_sectie, _ = VpbBoekSectie.objects.update_or_create(
                    hoofdstuk=current_hoofdstuk,
                    paragraaf=f"{nummer}.0",
                    defaults={"titel": titel, "order": sectie_order},
                )
                continue

            # Check Deel-kop: "## Deel A / Titel"
            deel_match = RE_DEEL.match(line)
            if deel_match and current_hoofdstuk:
                if current_text and current_sectie:
                    passage_order = self._save_passages(
                        current_sectie, current_text, current_page, passage_order
                    )
                    current_text = []

                sectie_order += 1
                passage_order = 0
                deel_letter = deel_match.group(1)
                titel = deel_match.group(2).strip()
                paragraaf = f"{current_hoofdstuk.nummer}{deel_letter}"

                current_sectie, _ = VpbBoekSectie.objects.update_or_create(
                    hoofdstuk=current_hoofdstuk,
                    paragraaf=paragraaf,
                    defaults={"titel": titel, "order": sectie_order},
                )
                continue

            # Check sectie: "## 2B.3.3 Art. 2..."
            sectie_match = RE_SECTIE.match(line)
            if sectie_match:
                code = sectie_match.group(1)
                titel = sectie_match.group(2).strip()

                # Detecteer hoofdstuk uit sectiecode als nog niet gezet
                ch_num = self._chapter_from_section_code(code)
                if ch_num and (current_hoofdstuk is None or current_hoofdstuk.nummer != ch_num):
                    # Flush
                    if current_text and current_sectie:
                        passage_order = self._save_passages(
                            current_sectie, current_text, current_page, passage_order
                        )
                        current_text = []
                    current_hoofdstuk = self._get_or_create_chapter(ch_num)
                    sectie_order = 0
                    passage_order = 0

                if current_hoofdstuk:
                    if current_text and current_sectie:
                        passage_order = self._save_passages(
                            current_sectie, current_text, current_page, passage_order
                        )
                        current_text = []

                    sectie_order += 1
                    passage_order = 0
                    current_sectie, _ = VpbBoekSectie.objects.update_or_create(
                        hoofdstuk=current_hoofdstuk,
                        paragraaf=code,
                        defaults={"titel": titel, "order": sectie_order},
                    )
                continue

            # Verzamel tekst (skip lege regels en page dividers)
            stripped = line.strip()
            if stripped and not stripped.startswith("---") and current_sectie:
                current_text.append(stripped)

        # Flush laatste tekst
        if current_text and current_sectie:
            self._save_passages(current_sectie, current_text, current_page, passage_order)

    def _save_passages(self, sectie, text_lines, page_num, start_order):
        """Splits tekst in passages en sla op."""
        full_text = " ".join(text_lines)
        words = full_text.split()

        if not words:
            return start_order

        order = start_order
        volgnummer = VpbBoekPassage.objects.filter(sectie=sectie).count()

        i = 0
        while i < len(words):
            chunk_words = words[i:i + MAX_PASSAGE_WORDS]
            if not chunk_words:
                break

            order += 1
            volgnummer += 1
            inhoud = " ".join(chunk_words)

            VpbBoekPassage.objects.update_or_create(
                sectie=sectie,
                volgnummer=volgnummer,
                defaults={
                    "inhoud": inhoud,
                    "pagina_start": page_num,
                    "order": order,
                },
            )

            i += MAX_PASSAGE_WORDS - OVERLAP_WORDS

        return order
