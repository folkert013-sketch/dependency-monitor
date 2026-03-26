"""
VPB Boek Knowledge Service — lookup in 'Wegwijs in de Vennootschapsbelasting'.

Voornamelijk semantic search (het boek heeft geen genummerde wetsartikelen).
"""

from dashboard.models import VpbBoekHoofdstuk, VpbBoekPassage


def _format_passage(passage, score=None):
    """Formatteer een passage als leesbare markdown."""
    sectie = passage.sectie
    header = f"**§ {sectie.paragraaf} — {sectie.titel}**"
    if sectie.hoofdstuk:
        header = f"**H{sectie.hoofdstuk.nummer}: {sectie.hoofdstuk.titel}** > {header}"
    if passage.pagina_start:
        header += f" (p. {passage.pagina_start})"
    if score is not None:
        header += f" (score: {score:.2f})"
    return f"{header}\n\n{passage.inhoud}"


class VpbBoekKnowledgeService:
    """Lookup in het VPB-boek: hoofdstuk match → vector search."""

    def lookup_by_hoofdstuk(self, query: str, editie: str = "") -> str | None:
        """Zoek op hoofdstuknaam/-nummer."""
        query_lower = query.lower().strip()

        qs = VpbBoekHoofdstuk.objects.prefetch_related("secties__passages")
        if editie:
            qs = qs.filter(editie=editie)
        hoofdstukken = qs

        for h in hoofdstukken:
            if h.nummer.lower() in query_lower or h.titel.lower() in query_lower:
                parts = [f"# H{h.nummer} — {h.titel}\n"]
                for sectie in h.secties.all():
                    parts.append(f"## § {sectie.paragraaf} — {sectie.titel}")
                    for p in sectie.passages.all()[:3]:
                        parts.append(p.inhoud[:500])
                        parts.append("")
                    total = sectie.passages.count()
                    if total > 3:
                        parts.append(f"*...en {total - 3} meer passages*")
                    parts.append("")
                return "\n".join(parts)

        return None

    def semantic_search(self, query: str, top_k: int = 8, editie: str = "") -> str | None:
        """Vector similarity search via pgvector."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return None

        base_filter = {"embedding__isnull": False}
        if editie:
            base_filter["sectie__hoofdstuk__editie"] = editie

        if not VpbBoekPassage.objects.filter(**base_filter).exists():
            return None

        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(query, normalize_embeddings=True).tolist()

        from pgvector.django import CosineDistance

        results = (
            VpbBoekPassage.objects.filter(**base_filter)
            .annotate(distance=CosineDistance("embedding", query_embedding))
            .order_by("distance")
            .select_related("sectie__hoofdstuk")[:top_k]
        )

        if not results:
            return None

        parts = [f"# Zoekresultaten (Wegwijs VPB) voor: *{query}*\n"]
        for p in results:
            score = 1 - p.distance
            parts.append(_format_passage(p, score=score))
            parts.append("\n---\n")

        return "\n".join(parts)

    def combined_lookup(self, query: str, editie: str = "") -> str:
        """Hoofdentry-point: hoofdstuk match → semantic search."""
        query = query.strip()
        if not query:
            return "Geef een onderwerp op (bijv. 'deelnemingsvrijstelling', 'innovatiebox')."

        # Parse editie uit query als '| 2025' formaat
        if not editie and "|" in query:
            parts = query.split("|", 1)
            query = parts[0].strip()
            editie = parts[1].strip()

        results = []

        # 1. Hoofdstuk match
        hoofdstuk = self.lookup_by_hoofdstuk(query, editie=editie)
        if hoofdstuk:
            results.append(hoofdstuk)

        # 2. Semantic search (altijd als aanvulling)
        if not hoofdstuk or len(hoofdstuk) < 500:
            semantic = self.semantic_search(query, top_k=8, editie=editie)
            if semantic:
                results.append(semantic)

        if not results:
            return (
                f"Geen informatie gevonden voor '{query}' in Wegwijs VPB. "
                "Probeer een ander onderwerp."
            )

        return "\n\n".join(results)
