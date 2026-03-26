"""
VPB Wet Knowledge Service — hybride lookup (exact + concept + vector).

Zoekt in officiële fiscale wetsartikelen (Wet Vpb 1969 e.a.).
"""

import re

from dashboard.models import FiscaalArtikel, FiscaalConceptMapping, FiscaalLid

# Regex voor wetsartikel-referenties
RE_ARTIKEL_LID = re.compile(
    r"(?:art\.?|artikel)\s*(\d+[a-z]*)\s*(?:lid\s*(\d+[a-z]?))?"
    r"(?:\s+(?:Wet\s*)?(?P<wet>vpb|db|awr|bvdb))?",
    re.I,
)
RE_WET_CODE = re.compile(r"\b(vpb|db|awr|bvdb)\b", re.I)


def _format_lid(lid, score=None):
    """Formatteer een lid als leesbare markdown."""
    art = lid.artikel
    header = f"**{art.referentie} lid {lid.nummer}**"
    if art.titel:
        header += f" — {art.titel}"
    if score is not None:
        header += f" (score: {score:.2f})"
    return f"{header}\n\n{lid.inhoud}"


def _format_artikel(artikel):
    """Formatteer een volledig artikel met al zijn leden."""
    lines = [f"## {artikel.referentie}"]
    if artikel.titel:
        lines[0] += f" — {artikel.titel}"
    lines.append("")
    for lid in artikel.leden.all():
        lines.append(f"**Lid {lid.nummer}**")
        lines.append(lid.inhoud)
        lines.append("")
    return "\n".join(lines)


def _wet_code_from_query(query):
    """Extraheer wet-code uit query, default naar vpb1969."""
    m = RE_WET_CODE.search(query)
    if m:
        mapping = {"vpb": "vpb1969", "db": "db1965", "awr": "awr", "bvdb": "bvdb2001"}
        return mapping.get(m.group(1).lower(), "vpb1969")
    return "vpb1969"


class VpbKnowledgeService:
    """Hybride VPB-wet lookup: exact match → concept → vector search."""

    def lookup_by_artikel(self, query: str, versie_datum: str = "") -> str | None:
        """Zoek op exact artikelnummer (art. 13 Vpb, artikel 20 lid 2)."""
        m = RE_ARTIKEL_LID.search(query)
        if not m:
            return None

        artikel_num = m.group(1)
        lid_num = m.group(2)
        wet_code = _wet_code_from_query(query)

        # Zoek artikel (met optioneel versie_datum filter)
        filters = {"nummer": artikel_num, "hoofdstuk__wet__code": wet_code}
        if versie_datum:
            filters["hoofdstuk__wet__versie_datum"] = versie_datum
        artikelen = FiscaalArtikel.objects.filter(
            **filters,
        ).select_related("hoofdstuk__wet").prefetch_related("leden")

        if not artikelen.exists():
            # Probeer zonder wet-filter (als gebruiker geen wet specificeerde)
            fallback_filters = {"nummer": artikel_num}
            if versie_datum:
                fallback_filters["hoofdstuk__wet__versie_datum"] = versie_datum
            artikelen = FiscaalArtikel.objects.filter(
                **fallback_filters,
            ).select_related("hoofdstuk__wet").prefetch_related("leden")

        if not artikelen.exists():
            return None

        parts = []
        for artikel in artikelen:
            if lid_num:
                # Specifiek lid
                leden = artikel.leden.filter(nummer=lid_num)
                if leden.exists():
                    for lid in leden:
                        parts.append(_format_lid(lid))
            else:
                # Heel artikel
                parts.append(_format_artikel(artikel))

        return "\n\n---\n\n".join(parts) if parts else None

    def lookup_by_concept(self, query: str, versie_datum: str = "") -> str | None:
        """Zoek via fiscaal concept mapping."""
        query_lower = query.lower()

        # Check concept_naam en trefwoorden
        mappings = FiscaalConceptMapping.objects.prefetch_related(
            "artikelen__hoofdstuk__wet", "artikelen__leden"
        )

        vpb_wet_codes = ["vpb1969", "db1965", "awr", "bvdb2001"]
        for mapping in mappings:
            # Filter op artikelen die bij VPB-gerelateerde wetten horen
            vpb_artikelen = [
                a for a in mapping.artikelen.all()
                if a.hoofdstuk.wet.code in vpb_wet_codes
                and (not versie_datum or a.hoofdstuk.wet.versie_datum == versie_datum)
            ]
            if not vpb_artikelen:
                continue

            naam_match = mapping.concept_naam.lower() in query_lower
            trefwoord_match = any(
                tw.strip() in query_lower
                for tw in mapping.trefwoorden.split(",")
                if tw.strip()
            )
            if naam_match or trefwoord_match:
                parts = [f"# Concept: {mapping.concept_naam}\n"]
                if mapping.beschrijving:
                    parts.append(f"*{mapping.beschrijving}*\n")
                for artikel in vpb_artikelen:
                    parts.append(_format_artikel(artikel))
                return "\n".join(parts)

        return None

    def semantic_search(self, query: str, top_k: int = 8, versie_datum: str = "") -> str | None:
        """Vector similarity search via pgvector."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return None

        vpb_wet_codes = ["vpb1969", "db1965", "awr", "bvdb2001"]
        base_filter = {
            "embedding__isnull": False,
            "artikel__hoofdstuk__wet__code__in": vpb_wet_codes,
        }
        if versie_datum:
            base_filter["artikel__hoofdstuk__wet__versie_datum"] = versie_datum

        if not FiscaalLid.objects.filter(**base_filter).exists():
            return None

        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(query, normalize_embeddings=True).tolist()

        from pgvector.django import CosineDistance

        results = (
            FiscaalLid.objects.filter(**base_filter)
            .annotate(distance=CosineDistance("embedding", query_embedding))
            .order_by("distance")
            .select_related("artikel__hoofdstuk__wet")[:top_k]
        )

        if not results:
            return None

        parts = [f"# Zoekresultaten voor: *{query}*\n"]
        for lid in results:
            score = 1 - lid.distance
            parts.append(_format_lid(lid, score=score))
            parts.append("\n---\n")

        return "\n".join(parts)

    def combined_lookup(self, query: str, versie_datum: str = "") -> str:
        """Hoofdentry-point: combineert alle zoekstrategieën.

        Args:
            query: Zoektekst (artikelnummer, concept of vraag).
            versie_datum: Optioneel versiedatum filter (bijv. '2025-01-01').
                         Laat leeg voor de meest recente versie.
        """
        query = query.strip()
        if not query:
            return (
                "Geef een wetsartikel (bijv. 'art. 13 Vpb'), "
                "een fiscaal concept (bijv. 'deelnemingsvrijstelling') "
                "of een vraag op."
            )

        # Parse versie_datum uit query als '| 2025' of '| 2025-01-01' formaat
        if not versie_datum and "|" in query:
            parts = query.split("|", 1)
            query = parts[0].strip()
            raw_versie = parts[1].strip()
            # Converteer kort jaar naar volledige datum
            if len(raw_versie) == 4 and raw_versie.isdigit():
                versie_datum = f"{raw_versie}-01-01"
            else:
                versie_datum = raw_versie

        results = []

        # 1. Exact match op artikelnummer
        exact = self.lookup_by_artikel(query, versie_datum=versie_datum)
        if exact:
            results.append(exact)

        # 2. Concept mapping
        concept = self.lookup_by_concept(query, versie_datum=versie_datum)
        if concept and not exact:
            results.append(concept)

        # 3. Semantic search (aanvulling)
        if not exact or len(exact) < 500:
            semantic = self.semantic_search(query, top_k=5, versie_datum=versie_datum)
            if semantic:
                results.append(semantic)

        if not results:
            return (
                f"Geen wetsartikelen gevonden voor '{query}'. "
                "Probeer een artikelnummer (art. 13 Vpb), een concept "
                "(deelnemingsvrijstelling, verliesverrekening) of een vraag."
            )

        return "\n\n".join(results)
