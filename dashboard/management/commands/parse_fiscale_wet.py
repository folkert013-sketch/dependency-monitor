"""
Parse fiscale wetgeving van wetten.overheid.nl XML naar database.

Ondersteunt Wet Vpb 1969 (en later DB, AWR, BVDB).
"""

import os
import xml.etree.ElementTree as ET

import requests
from django.core.management.base import BaseCommand

from dashboard.models import (
    FiscaalArtikel,
    FiscaalConceptMapping,
    FiscaalHoofdstuk,
    FiscaalLid,
    FiscaleWet,
)

# Bekende wetten met BWB-IDs
WETTEN = {
    "vpb1969": {
        "naam": "Wet op de vennootschapsbelasting 1969",
        "afkorting": "Wet Vpb 1969",
        "bwb_id": "BWBR0002672",
    },
    "db1965": {
        "naam": "Wet op de dividendbelasting 1965",
        "afkorting": "Wet DB 1965",
        "bwb_id": "BWBR0002515",
    },
    "awr": {
        "naam": "Algemene wet inzake rijksbelastingen",
        "afkorting": "AWR",
        "bwb_id": "BWBR0002320",
    },
    "bvdb2001": {
        "naam": "Besluit voorkoming dubbele belasting 2001",
        "afkorting": "BVDB 2001",
        "bwb_id": "BWBR0012095",
    },
    "ib2001": {
        "naam": "Wet inkomstenbelasting 2001",
        "afkorting": "Wet IB 2001",
        "bwb_id": "BWBR0011353",
    },
}

# Concept mappings: concept → lijst van (wet_code, artikel_nummer)
CONCEPT_MAPPINGS = {
    "Subjectieve belastingplicht": {
        "artikelen": [("vpb1969", "1"), ("vpb1969", "2"), ("vpb1969", "3")],
        "trefwoorden": "belastingplichtig,BV,NV,stichting,lichaam,subjectief",
        "beschrijving": "Welke lichamen zijn vpb-plichtig (binnenlands en buitenlands)",
    },
    "Winst": {
        "artikelen": [("vpb1969", "7"), ("vpb1969", "8")],
        "trefwoorden": "winst,totaalwinst,jaarwinst,goed koopmansgebruik,winstbepaling",
        "beschrijving": "Winstberekening en goed koopmansgebruik",
    },
    "Deelnemingsvrijstelling": {
        "artikelen": [("vpb1969", "13")],
        "trefwoorden": "deelneming,deelnemingsvrijstelling,kwalificerende deelneming,5%",
        "beschrijving": "Vrijstelling voor voordelen uit deelnemingen (art. 13)",
    },
    "Verliesverrekening": {
        "artikelen": [("vpb1969", "20")],
        "trefwoorden": "verlies,carry-forward,carry-back,verrekening,verliesverrekening",
        "beschrijving": "Voorwaartse en achterwaartse verliesverrekening",
    },
    "Fiscale eenheid": {
        "artikelen": [("vpb1969", "15")],
        "trefwoorden": "fiscale eenheid,consolidatie,voegingstijdstip,ontvoeging",
        "beschrijving": "Fiscale eenheid voor de vennootschapsbelasting",
    },
    "Earningsstripping / Renteaftrekbeperking": {
        "artikelen": [("vpb1969", "15b")],
        "trefwoorden": "renteaftrek,earningsstripping,EBITDA,thin cap,renteaftrekbeperking",
        "beschrijving": "Beperking van renteaftrek (earningsstrippingregeling)",
    },
    "Anti-misbruik renteaftrek": {
        "artikelen": [("vpb1969", "10a")],
        "trefwoorden": "10a,anti-misbruik,onzakelijke lening,gelieerde partij,rente",
        "beschrijving": "Niet-aftrekbare rente bij gelieerde verhoudingen",
    },
    "Innovatiebox": {
        "artikelen": [("vpb1969", "12b")],
        "trefwoorden": "innovatie,innovatiebox,patent,S&O,technologie,octrooibox",
        "beschrijving": "Verlaagd tarief voor winst uit innovatie",
    },
    "Transfer pricing": {
        "artikelen": [("vpb1969", "8b")],
        "trefwoorden": "verrekenprijzen,transfer pricing,arm's length,gelieerde partijen",
        "beschrijving": "Verrekenprijzen tussen gelieerde partijen",
    },
    "CFC-regeling": {
        "artikelen": [("vpb1969", "15ab")],
        "trefwoorden": "controlled foreign company,CFC,laagbelaste,buitenlandse",
        "beschrijving": "Controlled Foreign Company regeling (ATAD)",
    },
    "Liquidatieverlies": {
        "artikelen": [("vpb1969", "13d")],
        "trefwoorden": "liquidatie,liquidatieverlies,opheffing,deelneming",
        "beschrijving": "Aftrekbaar liquidatieverlies uit deelneming",
    },
    "VPB-tarief": {
        "artikelen": [("vpb1969", "22")],
        "trefwoorden": "tarief,percentage,schijf,belastbaar bedrag,laag tarief,hoog tarief",
        "beschrijving": "VPB-tarieven en schijven",
    },
    "Niet-aftrekbare kosten": {
        "artikelen": [("vpb1969", "10")],
        "trefwoorden": "niet-aftrekbaar,gemengde kosten,boete,steekpenningen",
        "beschrijving": "Kosten die niet in aftrek komen op de winst",
    },
    "Investeringsaftrek": {
        "artikelen": [("vpb1969", "8")],
        "trefwoorden": "investeringsaftrek,KIA,EIA,MIA,VAMIL,kleinschaligheid",
        "beschrijving": "Investeringsfaciliteiten (via art. 8 jo. Wet IB)",
    },
    "Afschrijvingen": {
        "artikelen": [("vpb1969", "8")],
        "trefwoorden": "afschrijving,bodemwaarde,goodwill,bedrijfsmiddel",
        "beschrijving": "Afschrijvingsregels voor de vennootschapsbelasting",
    },
    "Objectvrijstelling": {
        "artikelen": [("vpb1969", "15e")],
        "trefwoorden": "objectvrijstelling,buitenlandse winst,vaste inrichting",
        "beschrijving": "Objectvrijstelling voor buitenlandse winst",
    },
    "Voorzieningen": {
        "artikelen": [("vpb1969", "8")],
        "trefwoorden": "voorziening,Baksteenarrest,toekomstige uitgave,passivering",
        "beschrijving": "Fiscale voorzieningen en passiveringsregels",
    },
    "Herinvesteringsreserve": {
        "artikelen": [("vpb1969", "8")],
        "trefwoorden": "herinvesteringsreserve,HIR,boekwinst,vervangingsvoornemen",
        "beschrijving": "Doorschuiven van boekwinst bij herinvestering",
    },
    "Bronheffing rente en royalty's": {
        "artikelen": [("vpb1969", "15c"), ("vpb1969", "15d")],
        "trefwoorden": "bronheffing,conditionele bronbelasting,rente,royalty",
        "beschrijving": "Conditionele bronbelasting op rente en royalty's",
    },
    "Giftenaftrek": {
        "artikelen": [("vpb1969", "16")],
        "trefwoorden": "gift,giftenaftrek,ANBI,donatie",
        "beschrijving": "Giftenaftrek in de vennootschapsbelasting",
    },
    # --- Wet IB 2001 concepten ---
    "Box 1 — Werk en woning": {
        "artikelen": [("ib2001", "2.3"), ("ib2001", "3.1")],
        "trefwoorden": "box 1,werk en woning,belastbaar inkomen,winst uit onderneming",
        "beschrijving": "Belastbaar inkomen uit werk en woning (box 1)",
    },
    "Box 2 — Aanmerkelijk belang": {
        "artikelen": [("ib2001", "4.1"), ("ib2001", "4.6"), ("ib2001", "4.12")],
        "trefwoorden": "box 2,aanmerkelijk belang,ab,dga,5% belang,regulier voordeel,vervreemdingsvoordeel",
        "beschrijving": "Inkomsten uit aanmerkelijk belang (box 2)",
    },
    "Box 3 — Sparen en beleggen": {
        "artikelen": [("ib2001", "5.1"), ("ib2001", "5.2"), ("ib2001", "5.3")],
        "trefwoorden": "box 3,sparen,beleggen,forfaitair rendement,vermogensrendementsheffing",
        "beschrijving": "Belastbaar inkomen uit sparen en beleggen (box 3)",
    },
    "Heffingskortingen": {
        "artikelen": [("ib2001", "8.1"), ("ib2001", "8.10"), ("ib2001", "8.11")],
        "trefwoorden": "heffingskorting,algemene heffingskorting,arbeidskorting,ouderenkorting",
        "beschrijving": "Heffingskortingen (algemeen, arbeid, ouderen)",
    },
    "Ondernemersaftrek": {
        "artikelen": [("ib2001", "3.74"), ("ib2001", "3.76")],
        "trefwoorden": "ondernemersaftrek,zelfstandigenaftrek,startersaftrek,urencriterium",
        "beschrijving": "Zelfstandigenaftrek en startersaftrek voor IB-ondernemers",
    },
    "MKB-winstvrijstelling": {
        "artikelen": [("ib2001", "3.79a")],
        "trefwoorden": "mkb-winstvrijstelling,mkb,winstvrijstelling,14%",
        "beschrijving": "MKB-winstvrijstelling voor IB-ondernemers",
    },
    "Terbeschikkingstellingsregeling": {
        "artikelen": [("ib2001", "3.91"), ("ib2001", "3.92")],
        "trefwoorden": "terbeschikkingstelling,tbs,vermogensbestanddeel,resultaat overige werkzaamheden",
        "beschrijving": "TBS-regeling: vermogen ter beschikking stellen aan eigen BV",
    },
    "Persoonsgebonden aftrek": {
        "artikelen": [("ib2001", "6.1")],
        "trefwoorden": "persoonsgebonden aftrek,alimentatie,giften,zorgkosten,studiekosten",
        "beschrijving": "Persoonsgebonden aftrekposten in de IB",
    },
}


class Command(BaseCommand):
    help = "Parse fiscale wetgeving van wetten.overheid.nl XML"

    def add_arguments(self, parser):
        parser.add_argument(
            "--bwb-id",
            help="BWB-ID van de wet (bijv. BWBR0002672)",
        )
        parser.add_argument(
            "--code",
            help="Wet-code (bijv. vpb1969)",
        )
        parser.add_argument(
            "--file",
            help="Pad naar lokaal XML-bestand",
        )
        parser.add_argument(
            "--datum",
            default="2024-01-01",
            help="Geldigheidsdatum van de wet (default: 2024-01-01), bijv. 2025-01-01",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Verwijder bestaande data voor deze wet + datum",
        )

    def handle(self, *args, **options):
        bwb_id = options.get("bwb_id")
        code = options.get("code")
        file_path = options.get("file")
        clear = options["clear"]
        versie_datum = options.get("datum", "2024-01-01")

        # Bepaal welke wet
        wet_info = None
        if code and code in WETTEN:
            wet_info = WETTEN[code]
            wet_info["code"] = code
            bwb_id = bwb_id or wet_info["bwb_id"]
        elif bwb_id:
            for c, info in WETTEN.items():
                if info["bwb_id"] == bwb_id:
                    wet_info = {**info, "code": c}
                    break

        if not wet_info:
            self.stderr.write(self.style.ERROR(
                f"Onbekende wet. Gebruik --code ({', '.join(WETTEN.keys())}) "
                f"of --bwb-id"
            ))
            return

        # Haal XML op
        if file_path:
            if not os.path.isfile(file_path):
                self.stderr.write(self.style.ERROR(f"Bestand niet gevonden: {file_path}"))
                return
            with open(file_path, "r", encoding="utf-8") as f:
                xml_content = f.read()
        else:
            xml_content = self._fetch_xml(bwb_id, versie_datum)
            if not xml_content:
                return

        # Parse XML
        root = ET.fromstring(xml_content)

        # Maak of update wet (uniek per code + versie_datum)
        wet, _ = FiscaleWet.objects.update_or_create(
            code=wet_info["code"],
            versie_datum=versie_datum,
            defaults={
                "naam": wet_info["naam"],
                "afkorting": wet_info["afkorting"],
                "bwb_id": bwb_id or "",
            },
        )

        if clear:
            self.stdout.write(f"Bestaande data verwijderen voor {wet.afkorting} ({versie_datum})...")
            wet.hoofdstukken.all().delete()

        # Parse wetstructuur
        self._parse_wet(root, wet)

        # Seed concept mappings
        self._seed_concept_mappings()

        self.stdout.write(self.style.SUCCESS(
            f"Klaar: {wet.afkorting} — "
            f"{wet.hoofdstukken.count()} hoofdstukken, "
            f"{FiscaalArtikel.objects.filter(hoofdstuk__wet=wet).count()} artikelen, "
            f"{FiscaalLid.objects.filter(artikel__hoofdstuk__wet=wet).count()} leden"
        ))

    def _fetch_xml(self, bwb_id, versie_datum="2024-01-01"):
        """Haal wet-XML op van wetten.overheid.nl."""
        url = f"https://wetten.overheid.nl/{bwb_id}/{versie_datum}/0/xml"
        self.stdout.write(f"Ophalen: {url}")
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f"Fout bij ophalen: {e}"))
            return None

    def _parse_wet(self, root, wet):
        """Parse de XML-structuur van een wet.

        Structuur wetten.overheid.nl:
        <wettekst>
          <hoofdstuk>          ← Hoofdstuk I (direct artikelen)
            <artikel>...</artikel>
          </hoofdstuk>
          <hoofdstuk>          ← Hoofdstuk II (met afdelingen)
            <afdeling>         ← Afdeling 2.1
              <artikel>...</artikel>
            </afdeling>
          </hoofdstuk>
        """
        # Zoek <wettekst> element
        wettekst = root.find(".//wettekst")
        if wettekst is None:
            wettekst = root  # Fallback

        hoofdstuk_order = 0
        artikel_order = 0

        for hoofdstuk_el in self._direct_children(wettekst, "hoofdstuk"):
            hst_nr = self._get_kop_nr(hoofdstuk_el, "") or str(hoofdstuk_order + 1)
            hst_titel = self._get_kop_label(hoofdstuk_el, "") or f"Hoofdstuk {hst_nr}"

            # Check of dit hoofdstuk afdelingen heeft
            afdelingen = list(self._direct_children(hoofdstuk_el, "afdeling"))

            if afdelingen:
                # Hoofdstuk met afdelingen: maak per afdeling een FiscaalHoofdstuk
                for afd_el in afdelingen:
                    hoofdstuk_order += 1
                    afd_nr = self._get_kop_nr(afd_el, "") or str(hoofdstuk_order)
                    afd_titel = self._get_kop_label(afd_el, "") or ""
                    label = f"{hst_titel} — {afd_titel}" if afd_titel else hst_titel

                    hoofdstuk, _ = FiscaalHoofdstuk.objects.update_or_create(
                        wet=wet,
                        nummer=afd_nr,
                        defaults={"titel": label, "order": hoofdstuk_order},
                    )

                    # Artikelen in deze afdeling
                    for artikel_el in self._direct_children(afd_el, "artikel"):
                        artikel_order = self._parse_artikel(artikel_el, hoofdstuk, artikel_order)

                # Check ook artikelen direct onder het hoofdstuk (buiten afdelingen)
                for artikel_el in self._direct_children(hoofdstuk_el, "artikel"):
                    # Maak een hoofdstuk-record voor artikelen buiten afdelingen
                    hoofdstuk_order += 1
                    hst_db, _ = FiscaalHoofdstuk.objects.update_or_create(
                        wet=wet,
                        nummer=hst_nr,
                        defaults={"titel": hst_titel, "order": hoofdstuk_order},
                    )
                    artikel_order = self._parse_artikel(artikel_el, hst_db, artikel_order)
            else:
                # Hoofdstuk zonder afdelingen: artikelen direct onder hoofdstuk
                hoofdstuk_order += 1
                hoofdstuk, _ = FiscaalHoofdstuk.objects.update_or_create(
                    wet=wet,
                    nummer=hst_nr,
                    defaults={"titel": hst_titel, "order": hoofdstuk_order},
                )

                for artikel_el in self._direct_children(hoofdstuk_el, "artikel"):
                    artikel_order = self._parse_artikel(artikel_el, hoofdstuk, artikel_order)

        if hoofdstuk_order == 0:
            self.stdout.write("Geen hoofdstukken gevonden, zoek artikelen op top-level...")
            hoofdstuk, _ = FiscaalHoofdstuk.objects.update_or_create(
                wet=wet, nummer="I", defaults={"titel": wet.naam, "order": 1},
            )
            for artikel_el in wettekst.iter("artikel"):
                artikel_order = self._parse_artikel(artikel_el, hoofdstuk, artikel_order)

    def _parse_artikel(self, artikel_el, hoofdstuk, artikel_order):
        """Parse een enkel artikel-element."""
        artikel_order += 1
        art_nr = self._get_kop_nr(artikel_el, "") or str(artikel_order)
        art_titel = self._get_kop_label(artikel_el, "") or ""
        volledige_tekst = self._extract_text(artikel_el, "")

        artikel, _ = FiscaalArtikel.objects.update_or_create(
            hoofdstuk=hoofdstuk,
            nummer=art_nr,
            defaults={
                "titel": art_titel,
                "volledige_tekst": volledige_tekst,
                "order": artikel_order,
            },
        )

        # Parse leden (direct children)
        lid_order = 0
        for lid_el in self._direct_children(artikel_el, "lid"):
            lid_order += 1
            lid_nr = self._get_lid_nr(lid_el, "") or str(lid_order)
            lid_tekst = self._extract_text(lid_el, "")

            if lid_tekst.strip():
                FiscaalLid.objects.update_or_create(
                    artikel=artikel,
                    nummer=lid_nr,
                    defaults={"inhoud": lid_tekst.strip(), "order": lid_order},
                )

        # Als er geen leden zijn, maak één lid van de hele tekst
        if lid_order == 0 and volledige_tekst.strip():
            FiscaalLid.objects.update_or_create(
                artikel=artikel,
                nummer="1",
                defaults={"inhoud": volledige_tekst.strip(), "order": 1},
            )

        return artikel_order

    def _direct_children(self, parent, tag_name):
        """Vind alleen directe kinderen met een bepaalde tag (niet recursief)."""
        for child in parent:
            # Strip namespace
            local_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if local_tag == tag_name:
                yield child

    def _get_kop_nr(self, element, ns):
        """Haal het nummer uit een kop-element."""
        for kop in element.iter("kop"):
            for nr in kop.iter("nr"):
                return (nr.text or "").strip()
        return None

    def _get_kop_label(self, element, ns):
        """Haal de titel uit een kop-element."""
        for kop in element.iter("kop"):
            for titel in kop.iter("titel"):
                return (titel.text or "").strip()
        return None

    def _get_lid_nr(self, element, ns):
        """Haal lidnummer op."""
        for nr in element.iter("lidnr"):
            return (nr.text or "").strip().rstrip(".")
        return None

    def _extract_text(self, element, ns):
        """Extraheer alle tekst uit een element (recursief), skip meta-data."""
        parts = []
        for child in element.iter():
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            # Skip meta-data, kop en redactie elementen
            if tag in ("meta-data", "kop", "brondata", "jcis", "jci"):
                continue
            if child.text:
                stripped = child.text.strip()
                if stripped:
                    parts.append(stripped)
            if child.tail:
                stripped = child.tail.strip()
                if stripped:
                    parts.append(stripped)
        return " ".join(parts)

    def _seed_concept_mappings(self):
        """Maak concept mappings aan."""
        for concept_naam, info in CONCEPT_MAPPINGS.items():
            mapping, _ = FiscaalConceptMapping.objects.update_or_create(
                concept_naam=concept_naam,
                defaults={
                    "trefwoorden": info["trefwoorden"],
                    "beschrijving": info["beschrijving"],
                },
            )

            # Koppel artikelen
            artikel_pks = []
            for wet_code, art_nr in info["artikelen"]:
                try:
                    artikel = FiscaalArtikel.objects.get(
                        hoofdstuk__wet__code=wet_code,
                        nummer=art_nr,
                    )
                    artikel_pks.append(artikel.pk)
                except FiscaalArtikel.DoesNotExist:
                    pass  # Wet nog niet geladen
            if artikel_pks:
                mapping.artikelen.set(artikel_pks)
