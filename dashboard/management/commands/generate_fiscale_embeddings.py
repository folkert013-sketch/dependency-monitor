"""
Genereer vector embeddings voor fiscale wetsartikelen en/of VPB boekpassages.

Gebruikt all-MiniLM-L6-v2 (384 dimensies, meertalig, gratis, lokaal).
"""

from django.core.management.base import BaseCommand

from dashboard.models import FiscaalLid, VpbBoekPassage


class Command(BaseCommand):
    help = "Genereer vector embeddings voor fiscale wet-leden en/of VPB boekpassages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            choices=["wet", "boek", "all"],
            default="all",
            help="Welke bron: wet (wetsartikelen), boek (Wegwijs VPB), all (beide)",
        )
        parser.add_argument(
            "--model",
            default="all-MiniLM-L6-v2",
            help="Sentence-transformers model naam",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=64,
            help="Batch size voor embedding generatie",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overschrijf bestaande embeddings",
        )
        parser.add_argument(
            "--versie-datum",
            help="Alleen wet-leden van deze versiedatum embedden (bijv. 2025-01-01)",
        )
        parser.add_argument(
            "--editie",
            help="Alleen boekpassages van deze editie embedden (bijv. 2025)",
        )

    def handle(self, *args, **options):
        from sentence_transformers import SentenceTransformer

        source = options["source"]
        model_name = options["model"]
        batch_size = options["batch_size"]
        force = options["force"]
        versie_datum = options.get("versie_datum")
        editie = options.get("editie")

        self.stdout.write(f"Model laden: {model_name}...")
        model = SentenceTransformer(model_name)

        if source in ("wet", "all"):
            self._embed_wet(model, batch_size, force, versie_datum)

        if source in ("boek", "all"):
            self._embed_boek(model, batch_size, force, editie)

    def _embed_wet(self, model, batch_size, force, versie_datum=None):
        """Genereer embeddings voor FiscaalLid records."""
        qs = FiscaalLid.objects.select_related("artikel__hoofdstuk__wet")
        if versie_datum:
            qs = qs.filter(artikel__hoofdstuk__wet__versie_datum=versie_datum)
        if not force:
            qs = qs.filter(embedding__isnull=True)

        leden = list(qs)
        if not leden:
            self.stdout.write("Geen wet-leden om te embedden.")
            return

        self.stdout.write(f"Embeddings genereren voor {len(leden)} wet-leden...")

        texts = []
        for lid in leden:
            art = lid.artikel
            hst = art.hoofdstuk
            wet = hst.wet
            parts = [
                f"{wet.afkorting} | Hoofdstuk {hst.nummer}: {hst.titel}",
                f"Artikel {art.nummer}",
            ]
            if art.titel:
                parts[-1] += f": {art.titel}"
            parts.append(f"Lid {lid.nummer}: {lid.inhoud[:2000]}")
            texts.append(" | ".join(parts))

        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        for lid, emb in zip(leden, embeddings):
            lid.embedding = emb.tolist()

        FiscaalLid.objects.bulk_update(leden, ["embedding"], batch_size=100)
        self.stdout.write(self.style.SUCCESS(f"Klaar: {len(leden)} wet-embeddings opgeslagen"))

    def _embed_boek(self, model, batch_size, force, editie=None):
        """Genereer embeddings voor VpbBoekPassage records."""
        qs = VpbBoekPassage.objects.select_related("sectie__hoofdstuk")
        if editie:
            qs = qs.filter(sectie__hoofdstuk__editie=editie)
        if not force:
            qs = qs.filter(embedding__isnull=True)

        passages = list(qs)
        if not passages:
            self.stdout.write("Geen boekpassages om te embedden.")
            return

        self.stdout.write(f"Embeddings genereren voor {len(passages)} boekpassages...")

        texts = []
        for p in passages:
            sectie = p.sectie
            hst = sectie.hoofdstuk
            parts = [
                f"Wegwijs VPB | H{hst.nummer}: {hst.titel}",
                f"§ {sectie.paragraaf}: {sectie.titel}",
                p.inhoud[:2000],
            ]
            texts.append(" | ".join(parts))

        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        for passage, emb in zip(passages, embeddings):
            passage.embedding = emb.tolist()

        VpbBoekPassage.objects.bulk_update(passages, ["embedding"], batch_size=100)
        self.stdout.write(self.style.SUCCESS(f"Klaar: {len(passages)} boek-embeddings opgeslagen"))
