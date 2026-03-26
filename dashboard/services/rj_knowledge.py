"""
RJ Richtlijnen Knowledge Service — hybride lookup (exact + rubriek + vector).

Combineert Django ORM queries met pgvector cosine similarity search.
"""

import re

from django.db.models import Q

from dashboard.models import RJAlinea, RJHoofdstuk, RJRubriekMapping, RJSectie

# Regex voor RJ-referenties
RE_CODE_FULL = re.compile(r"(?:RJ\s*)?([A-Z]\d+)\.(\d+)\.(\d+[a-z]?)", re.I)  # B2.1.101
RE_CODE_SECTION = re.compile(r"(?:RJ\s*)?([A-Z]\d+)\.(\d+)", re.I)  # B2.1
RE_CODE_CHAPTER = re.compile(r"(?:RJ\s*)?([A-Z]\d+)\b", re.I)  # B2


def _format_alinea(alinea, score=None):
    """Formatteer een alinea als leesbare markdown."""
    ref = f"{alinea.sectie.paragraaf}.{alinea.nummer}"
    header = f"**{ref}** — {alinea.sectie.hoofdstuk.titel}"
    if alinea.sub_onderwerp:
        header += f" > {alinea.sub_onderwerp}"
    if score is not None:
        header += f" (score: {score:.2f})"
    return f"{header}\n\n{alinea.inhoud}"


def _format_section_summary(sectie, alineas):
    """Formatteer een sectie met al haar alinea's."""
    lines = [f"## § {sectie.paragraaf} — {sectie.titel}\n"]
    for a in alineas:
        lines.append(f"**Alinea {a.nummer}**")
        if a.sub_onderwerp:
            lines.append(f"*{a.sub_onderwerp}*")
        lines.append(a.inhoud)
        lines.append("")
    return "\n".join(lines)


class RJKnowledgeService:
    """Hybride RJ-richtlijnen lookup: exact match → rubriek → vector search."""

    def lookup_by_code(self, query: str) -> str | None:
        """Zoek op exacte RJ-code (B2, B2.1, B2.1.101)."""
        query = query.strip()

        # Probeer volledige referentie: B2.1.101
        m = RE_CODE_FULL.search(query)
        if m:
            chapter_code = m.group(1).upper()
            section_num = m.group(2)
            alinea_num = m.group(3)
            paragraaf = f"{chapter_code}.{section_num}"
            alineas = RJAlinea.objects.filter(
                sectie__paragraaf__iexact=paragraaf,
                nummer=alinea_num,
            ).select_related("sectie__hoofdstuk")
            if alineas.exists():
                return "\n\n---\n\n".join(_format_alinea(a) for a in alineas)

        # Probeer sectie: B2.1
        m = RE_CODE_SECTION.search(query)
        if m:
            chapter_code = m.group(1).upper()
            section_num = m.group(2)
            paragraaf = f"{chapter_code}.{section_num}"
            secties = RJSectie.objects.filter(
                paragraaf__iexact=paragraaf,
            ).prefetch_related("alineas")
            for sectie in secties:
                alineas = sectie.alineas.all()
                if alineas.exists():
                    return _format_section_summary(sectie, alineas)

        # Probeer hoofdstuk: B2
        m = RE_CODE_CHAPTER.search(query)
        if m:
            code = m.group(1).upper()
            try:
                hoofdstuk = RJHoofdstuk.objects.get(code__iexact=code)
            except RJHoofdstuk.DoesNotExist:
                return None

            secties = hoofdstuk.secties.prefetch_related("alineas").all()
            if not secties.exists():
                return None

            parts = [f"# {hoofdstuk.code} — {hoofdstuk.titel}\n"]
            if hoofdstuk.beschrijving:
                parts.append(f"*{hoofdstuk.beschrijving[:500]}*\n")
            for sectie in secties:
                alineas = sectie.alineas.all()[:5]  # Max 5 per sectie voor overzicht
                parts.append(f"## § {sectie.paragraaf} — {sectie.titel}")
                for a in alineas:
                    parts.append(f"- **{a.nummer}**: {a.inhoud[:200]}...")
                total = sectie.alineas.count()
                if total > 5:
                    parts.append(f"  *...en {total - 5} meer alinea's*")
                parts.append("")
            return "\n".join(parts)

        return None

    def lookup_by_rubriek(self, query: str) -> str | None:
        """Zoek op jaarrekening-rubriek via RJRubriekMapping."""
        query_lower = query.lower()

        # Filter matching mappings first, then prefetch only for those
        all_names = RJRubriekMapping.objects.values_list("pk", "rubriek_naam")
        matching_pks = [pk for pk, naam in all_names if naam.lower() in query_lower]
        if not matching_pks:
            return None

        mappings = RJRubriekMapping.objects.filter(pk__in=matching_pks).prefetch_related(
            "hoofdstukken__secties__alineas"
        )

        for mapping in mappings:
            parts = [f"# Rubriek: {mapping.rubriek_naam}\n"]
            for hoofdstuk in mapping.hoofdstukken.all():
                parts.append(f"## {hoofdstuk.code} — {hoofdstuk.titel}")
                for sectie in hoofdstuk.secties.all():
                    alineas = sectie.alineas.all()
                    if alineas.exists():
                        parts.append(f"\n### § {sectie.paragraaf} — {sectie.titel}\n")
                        for a in alineas[:10]:
                            parts.append(f"**{a.nummer}** {a.inhoud[:300]}")
                            parts.append("")
                        total = alineas.count()
                        if total > 10:
                            parts.append(f"*...en {total - 10} meer alinea's*\n")
            return "\n".join(parts)

        return None

    def semantic_search(self, query: str, top_k: int = 8) -> str | None:
        """Vector similarity search via pgvector."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return None

        # Check of er embeddings zijn
        if not RJAlinea.objects.filter(embedding__isnull=False).exists():
            return None

        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(query, normalize_embeddings=True).tolist()

        # pgvector cosine distance search (lager = beter)
        from pgvector.django import CosineDistance

        results = (
            RJAlinea.objects.filter(embedding__isnull=False)
            .annotate(distance=CosineDistance("embedding", query_embedding))
            .order_by("distance")
            .select_related("sectie__hoofdstuk")[:top_k]
        )

        if not results:
            return None

        parts = [f"# Zoekresultaten voor: *{query}*\n"]
        for a in results:
            score = 1 - a.distance  # Convert distance to similarity
            parts.append(_format_alinea(a, score=score))
            parts.append("\n---\n")

        return "\n".join(parts)

    def combined_lookup(self, query: str) -> str:
        """
        Hoofdentry-point: combineert alle zoekstrategieën.

        Volgorde: exact code → rubriek mapping → semantic search.
        """
        query = query.strip()
        if not query:
            return "Geef een RJ-code (bijv. B2, B2.1, B2.1.101), een rubriek (bijv. voorraden) of een vraag op."

        results = []

        # 1. Exact match op code
        exact = self.lookup_by_code(query)
        if exact:
            results.append(exact)

        # 2. Rubriek mapping
        rubriek = self.lookup_by_rubriek(query)
        if rubriek and not exact:
            results.append(rubriek)

        # 3. Semantic search (altijd als aanvulling, tenzij exact al veel gaf)
        if not exact or len(exact) < 500:
            semantic = self.semantic_search(query, top_k=5)
            if semantic:
                results.append(semantic)

        if not results:
            return (
                f"Geen RJ-richtlijnen gevonden voor '{query}'. "
                "Probeer een RJ-code (B2, B4.1), een rubriek (voorraden, eigen vermogen) "
                "of een inhoudelijke vraag."
            )

        return "\n\n".join(results)
