"""
Parse de OCR-gegenereerde RJ markdown naar gestructureerde database records.

Leest docs/rj_richtlijnen.md en maakt RJHoofdstuk, RJSectie en RJAlinea records.
"""

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import RJAlinea, RJHoofdstuk, RJRubriekMapping, RJSectie

# Hoofdstukken uit de inhoudsopgave met hun titels en afdeling
CHAPTERS = {
    "M1": ("Microrechtspersonen", "M"),
    "A1": ("Inleiding, status, doelstellingen en uitgangspunten", "A"),
    "A2": ("Verwerking en waardering", "A"),
    "A3": ("Stelselwijzigingen, schattingswijzigingen en foutenhersstel", "A"),
    "A4": ("Gebeurtenissen na balansdatum", "A"),
    "A5": ("Verbonden partijen", "A"),
    "A6": ("Openbaarmaking", "A"),
    "A7": ("Overige gegevens", "A"),
    "A8": ("Winstbestemming en verwerking van het verlies", "A"),
    "B1": ("Immateriële vaste activa", "B"),
    "B2": ("Materiële vaste activa en vastgoedbeleggingen", "B"),
    "B3": ("Financiële vaste activa en consolidatie", "B"),
    "B4": ("Voorraden", "B"),
    "B5": ("Vorderingen en overlopende activa", "B"),
    "B6": ("Effecten", "B"),
    "B7": ("Liquide middelen", "B"),
    "B8": ("Eigen vermogen", "B"),
    "B9": ("Verplichtingen en schulden", "B"),
    "B10": ("Voorzieningen en niet in de balans opgenomen verplichtingen", "B"),
    "B11": ("Leasing", "B"),
    "B12": ("Financiële instrumenten", "B"),
    "B13": ("Winst-en-verliesrekening", "B"),
    "B14": ("Personeelsbeloningen", "B"),
    "B15": ("Belastingen naar de winst", "B"),
    "B16": ("Rente", "B"),
    "B17": ("Overheidssubsidies en andere vormen van overheidssteun", "B"),
    "B18": ("Toelichting", "B"),
    "C1": ("Kleine organisaties-zonder-winststreven", "C"),
    "C2": ("Kleine fondsenwervende organisaties", "C"),
    "C3": ("Kleine zorgaanbieders", "C"),
    "D1": ("Wetteksten", "D"),
    "D2": ("Modellen en besluiten", "D"),
    "D3": ("Handreikingen", "D"),
    "D4": ("Inrichtings- en publicatievoorschriften", "D"),
}

# Secties uit de inhoudsopgave
SECTIONS = {
    "M1.1": "Algemene uiteenzettingen",
    "M1.2": "Presentatie en toelichting",
    "M1.3": "Verwerking en waardering",
    "M1.4": "Openbaarmaking",
    "A1.1": "Inleiding",
    "A1.2": "Status van de Richtlijnen",
    "A1.3": "Doelstellingen en uitgangspunten",
    "A2.1": "Criteria voor opname en vermelding van gegevens",
    "A2.2": "Prijsgrondslagen",
    "A2.3": "Bijzondere waardeverminderingen van vaste activa",
    "A2.4": "Prijsgrondslagen voor vreemde valuta transacties",
    "A2.5": "Algemene grondslagen voor de bepaling van het resultaat",
    "A3.1": "Stelselwijzigingen",
    "A3.2": "Schattingswijzigingen",
    "A3.3": "Foutenhersstel",
    "B2.1": "Materiële vaste activa",
    "B2.2": "Vastgoedbeleggingen",
    "B3.1": "Financiële vaste activa",
    "B3.2": "Fusies en overnames",
    "B3.3": "Consolidatie",
    "B3.4": "Verwerking van resultaten op intercompany-transacties",
    "B4.1": "Algemeen",
    "B4.2": "Onderhanden projecten in opdracht van derden",
    "B5.1": "Vorderingen",
    "B5.2": "Overlopende activa",
    "B5.3": "Onderhanden projecten",
    "B9.1": "Algemeen",
    "B9.2": "Langlopende schulden",
    "B9.3": "Kortlopende schulden",
    "B9.4": "Overlopende passiva",
    "B10.1": "Voorzieningen",
    "B10.2": "Niet in de balans opgenomen verplichtingen",
    "B18.1": "Algemeen",
    "B18.2": "Beëindiging van bedrijfsactiviteiten",
    "B18.3": "Dienstverlening uit hoofde van concessies",
    "C1.1": "Algemene uiteenzettingen",
    "C1.2": "Verwerking en waardering",
    "C1.3": "Presentatie en toelichting",
    "C1.4": "Bijzondere onderwerpen",
    "C1.5": "Overgangsbepaling",
    "C2.1": "Algemene uiteenzettingen",
    "C2.2": "Verwerking en waardering",
    "C2.3": "Presentatie en toelichting",
    "C2.4": "Bijzondere onderwerpen",
    "C3.1": "Algemene uiteenzettingen",
    "C3.2": "Verwerking en waardering",
    "C3.3": "Presentatie",
    "C3.4": "Toelichting",
    "C3.5": "Bijzondere onderwerpen",
    "D1.1": "Tekst van Titel 9 Boek 2 BW",
    "D1.2": "Tekst van diverse artikelen Boek 2 BW",
    "D1.3": "Tekst van enkele artikelen van de Handelsregisterwet 2007",
    "D2.1": "Besluit modellen jaarrekening",
    "D2.2": "Besluit actuele waarde",
    "D2.3": "Besluit fiscale waarderingsgrondslagen",
    "D2.4": "Besluit wijziging besluiten 2015",
    "D2.5": "Uitvoeringswet richtlijn jaarrekening",
    "D2.6": "Besluit elektronische deponering handelsregister",
    "D3.1": "Handreiking fiscale waarderingsgrondslagen microrechtspersonen",
    "D3.2": "Handreiking fiscale waarderingsgrondslagen kleine rechtspersonen",
}

# Standaard rubriek-mappings
RUBRIEK_MAPPINGS = {
    "Immateriële vaste activa": ["B1"],
    "Materiële vaste activa": ["B2"],
    "Vastgoedbeleggingen": ["B2"],
    "Financiële vaste activa": ["B3"],
    "Voorraden": ["B4"],
    "Vorderingen": ["B5"],
    "Overlopende activa": ["B5"],
    "Onderhanden projecten": ["B5"],
    "Effecten": ["B6"],
    "Liquide middelen": ["B7"],
    "Eigen vermogen": ["B8"],
    "Schulden": ["B9"],
    "Langlopende schulden": ["B9"],
    "Kortlopende schulden": ["B9"],
    "Voorzieningen": ["B10"],
    "Leasing": ["B11"],
    "Financiële instrumenten": ["B12"],
    "Winst-en-verliesrekening": ["B13"],
    "Personeelsbeloningen": ["B14"],
    "Belastingen naar de winst": ["B15"],
    "Rente": ["B16"],
    "Overheidssubsidies": ["B17"],
    "Afschrijvingen": ["B2", "B1"],
    "Waarderingsgrondslagen": ["A2"],
    "Stelselwijzigingen": ["A3"],
    "Gebeurtenissen na balansdatum": ["A4"],
    "Openbaarmaking": ["A6"],
    "Continuïteit": ["A1"],
    "Microrechtspersonen": ["M1"],
}

# Regex patronen
RE_PAGE_MARKER = re.compile(r"^--- Pagina \d+ ---$")
RE_WATERMARK = re.compile(r"^\[WKNL-EY\]$")
RE_IMAGE = re.compile(r"^!\[.*\]\(.*\)$")
RE_PAGE_HEADER = re.compile(r"^Hoofdstuk [A-Z]\d+")
RE_CHAPTER_START = re.compile(r"^([A-Z]\d+)\s+[A-Z]")
RE_SECTION_CODE = re.compile(r"^([A-Z]\d+\.\d+)\s*$")
RE_SECTION_TITLED = re.compile(r"^([A-Z]\d+\.\d+)\s+([A-Z].+)$")
RE_ALINEA_START = re.compile(r"^(\d+[a-z]?)\s+(.+)")
RE_SUB_HEADER = re.compile(r"^##\s+(.+)$")
RE_TOC_LINE = re.compile(r"^[A-Z]\d+.*/ \d+$")
RE_TOC_SUB = re.compile(r"^[-§]")


def clean_lines(raw_text: str) -> list[str]:
    """Verwijder artefacten en geef schone regels terug."""
    lines = raw_text.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append("")
            continue
        if RE_PAGE_MARKER.match(stripped):
            continue
        if RE_WATERMARK.match(stripped):
            continue
        if RE_IMAGE.match(stripped):
            continue
        if RE_PAGE_HEADER.match(stripped):
            continue
        if stripped == "INHOUDSOPGAVE":
            continue
        cleaned.append(stripped)
    return cleaned


def find_content_start(lines: list[str]) -> int:
    """Vind waar de daadwerkelijke content begint (na inhoudsopgave/voorwoord)."""
    for i, line in enumerate(lines):
        if line == "M1 MICRORECHTSPERSONEN":
            return i
    # Fallback: zoek eerste hoofdstuk-achtige lijn na regel 300
    for i, line in enumerate(lines[300:], start=300):
        m = RE_CHAPTER_START.match(line)
        if m and m.group(1) in CHAPTERS:
            return i
    return 0


class Command(BaseCommand):
    help = "Parse de RJ markdown naar database records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=str(settings.BASE_DIR / "docs" / "rj_richtlijnen.md"),
            help="Pad naar de RJ markdown file",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Verwijder bestaande RJ data voor het laden",
        )

    def handle(self, *args, **options):
        md_path = Path(options["file"])
        if not md_path.is_file():
            self.stderr.write(f"Bestand niet gevonden: {md_path}")
            return

        if options["clear"]:
            count = RJAlinea.objects.count()
            RJAlinea.objects.all().delete()
            RJSectie.objects.all().delete()
            RJHoofdstuk.objects.all().delete()
            RJRubriekMapping.objects.all().delete()
            self.stdout.write(f"Verwijderd: {count} alinea's + hoofdstukken + secties + mappings")

        raw_text = md_path.read_text(encoding="utf-8")
        lines = clean_lines(raw_text)
        start_idx = find_content_start(lines)
        self.stdout.write(f"Content start op regel {start_idx}: {lines[start_idx][:60]}")

        # Stap 1: Maak hoofdstukken aan
        hoofdstukken = {}
        for order, (code, (titel, afdeling)) in enumerate(CHAPTERS.items()):
            obj, created = RJHoofdstuk.objects.update_or_create(
                code=code,
                defaults={
                    "titel": titel,
                    "afdeling": afdeling,
                    "order": order,
                },
            )
            hoofdstukken[code] = obj
            if created:
                self.stdout.write(f"  + Hoofdstuk {code}: {titel}")

        # Stap 2: Maak secties aan
        secties = {}
        for order, (paragraaf, titel) in enumerate(SECTIONS.items()):
            chapter_code = re.match(r"([A-Z]\d+)\.", paragraaf).group(1)
            hoofdstuk = hoofdstukken.get(chapter_code)
            if not hoofdstuk:
                continue
            obj, created = RJSectie.objects.update_or_create(
                hoofdstuk=hoofdstuk,
                paragraaf=paragraaf,
                defaults={"titel": titel, "order": order},
            )
            secties[paragraaf] = obj

        # Maak default secties voor hoofdstukken zonder sub-secties
        for code, hoofdstuk in hoofdstukken.items():
            has_sections = any(k.startswith(code + ".") for k in SECTIONS)
            if not has_sections:
                key = f"{code}.0"
                obj, _ = RJSectie.objects.update_or_create(
                    hoofdstuk=hoofdstuk,
                    paragraaf=key,
                    defaults={"titel": hoofdstuk.titel, "order": 0},
                )
                secties[key] = obj

        self.stdout.write(f"Hoofdstukken: {len(hoofdstukken)}, Secties: {len(secties)}")

        # Stap 3: Parse alinea's
        current_chapter = None
        current_section = None
        current_alinea_num = None
        current_alinea_text = []
        current_sub = ""
        alinea_order = 0
        alineas_created = 0
        skipped_lines = 0

        def flush_alinea():
            nonlocal current_alinea_num, current_alinea_text, alinea_order, alineas_created
            if current_alinea_num and current_section and current_alinea_text:
                text = "\n".join(current_alinea_text).strip()
                if text:
                    RJAlinea.objects.update_or_create(
                        sectie=current_section,
                        nummer=current_alinea_num,
                        defaults={
                            "inhoud": text,
                            "sub_onderwerp": current_sub,
                            "order": alinea_order,
                        },
                    )
                    alineas_created += 1
                    alinea_order += 1
            current_alinea_num = None
            current_alinea_text = []

        i = start_idx
        while i < len(lines):
            line = lines[i]
            i += 1

            # Lege regels → onderdeel van huidige alinea
            if not line:
                if current_alinea_text:
                    current_alinea_text.append("")
                continue

            # Inhoudsopgave-regels overslaan
            if RE_TOC_LINE.match(line) or RE_TOC_SUB.match(line):
                continue

            # Hoofdstuk-start detecteren
            m = RE_CHAPTER_START.match(line)
            if m:
                code = m.group(1)
                if code in hoofdstukken:
                    flush_alinea()
                    current_chapter = code
                    # Zoek de default sectie of eerste sectie
                    default_key = f"{code}.0"
                    if default_key in secties:
                        current_section = secties[default_key]
                    else:
                        # Pak de eerste sectie van dit hoofdstuk
                        first_key = next(
                            (k for k in secties if k.startswith(code + ".")),
                            None,
                        )
                        if first_key:
                            current_section = secties[first_key]
                    alinea_order = 0
                    current_sub = ""
                    # Beschrijving opslaan (volgende niet-lege regel)
                    desc_lines = []
                    while i < len(lines) and lines[i]:
                        next_line = lines[i]
                        # Stop als het een sectie-header of alinea-nummer is
                        if RE_SECTION_TITLED.match(next_line):
                            break
                        if RE_SECTION_CODE.match(next_line):
                            break
                        if RE_ALINEA_START.match(next_line):
                            break
                        if RE_CHAPTER_START.match(next_line):
                            break
                        desc_lines.append(next_line)
                        i += 1
                    if desc_lines:
                        h = hoofdstukken[code]
                        h.beschrijving = "\n".join(desc_lines)
                        h.save(update_fields=["beschrijving"])
                    continue

            # Sectie met titel
            m = RE_SECTION_TITLED.match(line)
            if m:
                code = m.group(1)
                if code in secties:
                    flush_alinea()
                    current_section = secties[code]
                    alinea_order = 0
                    current_sub = ""
                    continue

            # Sectie-code alleen (page header) → update huidige sectie
            m = RE_SECTION_CODE.match(line)
            if m:
                code = m.group(1)
                if code in secties:
                    current_section = secties[code]
                continue

            # Sub-header (## Afschrijvingen)
            m = RE_SUB_HEADER.match(line)
            if m:
                flush_alinea()
                current_sub = m.group(1).strip()
                continue

            # Alinea-start (101 Voorraden zijn activa...)
            m = RE_ALINEA_START.match(line)
            if m and current_section:
                num = m.group(1)
                rest = m.group(2)
                # Alleen nummers die typisch RJ-alineanummers zijn (100-999 of 1-99 met context)
                if num.isdigit() and (100 <= int(num) <= 999 or (current_chapter and int(num) < 100)):
                    flush_alinea()
                    current_alinea_num = num
                    current_alinea_text = [rest]
                    continue
                # Nummers met letter suffix (102a, 133d)
                if re.match(r"\d+[a-z]$", num):
                    flush_alinea()
                    current_alinea_num = num
                    current_alinea_text = [rest]
                    continue

            # Anders: toevoegen aan huidige alinea
            if current_alinea_text is not None:
                current_alinea_text.append(line)
            else:
                skipped_lines += 1

        # Laatste alinea flushen
        flush_alinea()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nResultaat: {alineas_created} alinea's aangemaakt "
                f"({skipped_lines} regels overgeslagen)"
            )
        )

        # Stap 4: Rubriek-mappings aanmaken
        mappings_created = 0
        for naam, codes in RUBRIEK_MAPPINGS.items():
            obj, _ = RJRubriekMapping.objects.get_or_create(rubriek_naam=naam)
            for code in codes:
                if code in hoofdstukken:
                    obj.hoofdstukken.add(hoofdstukken[code])
            mappings_created += 1

        self.stdout.write(self.style.SUCCESS(f"Rubriek-mappings: {mappings_created}"))
