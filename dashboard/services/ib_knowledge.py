"""
IB Wet Knowledge Service — hybride lookup (exact + concept + vector).

Zoekt in officiële fiscale wetsartikelen (Wet IB 2001).
"""

import re

from dashboard.models import FiscaalArtikel, FiscaalConceptMapping, FiscaalLid

# Regex voor IB-artikelverwijzingen (bijv. "art. 3.1 IB", "artikel 4.12 lid 2")
RE_ARTIKEL_LID = re.compile(
    r"(?:art\.?|artikel)\s*(\d+(?:\.\d+[a-z]*)?)\s*(?:lid\s*(\d+[a-z]?))?",
    re.I,
)


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


class IbKnowledgeService:
    """Hybride IB-wet lookup: exact match → concept → vector search."""

    WET_CODE = "ib2001"

    def lookup_by_artikel(self, query: str) -> str | None:
        """Zoek op exact artikelnummer (art. 3.1 IB, artikel 4.12 lid 2)."""
        m = RE_ARTIKEL_LID.search(query)
        if not m:
            return None

        artikel_num = m.group(1)
        lid_num = m.group(2)

        artikelen = FiscaalArtikel.objects.filter(
            nummer=artikel_num,
            hoofdstuk__wet__code=self.WET_CODE,
        ).select_related("hoofdstuk__wet").prefetch_related("leden")

        if not artikelen.exists():
            return None

        parts = []
        for artikel in artikelen:
            if lid_num:
                leden = artikel.leden.filter(nummer=lid_num)
                if leden.exists():
                    for lid in leden:
                        parts.append(_format_lid(lid))
            else:
                parts.append(_format_artikel(artikel))

        return "\n\n---\n\n".join(parts) if parts else None

    def lookup_by_concept(self, query: str) -> str | None:
        """Zoek via fiscaal concept mapping (alleen IB-gerelateerde concepten)."""
        query_lower = query.lower()

        mappings = FiscaalConceptMapping.objects.prefetch_related(
            "artikelen__hoofdstuk__wet", "artikelen__leden"
        )

        for mapping in mappings:
            # Filter op artikelen die bij IB horen
            ib_artikelen = [
                a for a in mapping.artikelen.all()
                if a.hoofdstuk.wet.code == self.WET_CODE
            ]
            if not ib_artikelen:
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
                for artikel in ib_artikelen:
                    parts.append(_format_artikel(artikel))
                return "\n".join(parts)

        return None

    def semantic_search(self, query: str, top_k: int = 8) -> str | None:
        """Vector similarity search via pgvector — alleen IB-artikelen."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return None

        if not FiscaalLid.objects.filter(
            embedding__isnull=False,
            artikel__hoofdstuk__wet__code=self.WET_CODE,
        ).exists():
            return None

        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(query, normalize_embeddings=True).tolist()

        from pgvector.django import CosineDistance

        results = (
            FiscaalLid.objects.filter(
                embedding__isnull=False,
                artikel__hoofdstuk__wet__code=self.WET_CODE,
            )
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
        """Hoofdentry-point: combineert alle zoekstrategieën."""
        query = query.strip()
        if not query:
            return (
                "Geef een wetsartikel (bijv. 'art. 3.1 IB'), "
                "een fiscaal concept (bijv. 'box 2', 'zelfstandigenaftrek') "
                "of een vraag op."
            )

        # Parse versie_datum uit query als '| 2025' formaat
        if not versie_datum and "|" in query:
            parts = query.split("|", 1)
            query = parts[0].strip()
            raw_versie = parts[1].strip()
            if len(raw_versie) == 4 and raw_versie.isdigit():
                versie_datum = f"{raw_versie}-01-01"
            else:
                versie_datum = raw_versie

        results = []

        # 1. Exact match op artikelnummer
        exact = self.lookup_by_artikel(query)
        if exact:
            results.append(exact)

        # 2. Concept mapping
        concept = self.lookup_by_concept(query)
        if concept and not exact:
            results.append(concept)

        # 3. Semantic search (aanvulling)
        if not exact or len(exact) < 500:
            semantic = self.semantic_search(query, top_k=5)
            if semantic:
                results.append(semantic)

        if not results:
            return (
                f"Geen wetsartikelen gevonden voor '{query}'. "
                "Probeer een artikelnummer (art. 3.1 IB), een concept "
                "(box 2, zelfstandigenaftrek, heffingskorting) of een vraag."
            )

        return "\n\n".join(results)
