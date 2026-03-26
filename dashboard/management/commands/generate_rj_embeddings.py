"""
Genereer vector embeddings voor alle RJ-alinea's met sentence-transformers.

Gebruikt all-MiniLM-L6-v2 (384 dimensies, meertalig, gratis, lokaal).
Slaat embeddings op in het pgvector VectorField.
"""

from django.core.management.base import BaseCommand

from dashboard.models import RJAlinea


class Command(BaseCommand):
    help = "Genereer vector embeddings voor RJ-alinea's"

    def add_arguments(self, parser):
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

    def handle(self, *args, **options):
        from sentence_transformers import SentenceTransformer

        model_name = options["model"]
        batch_size = options["batch_size"]
        force = options["force"]

        # Selecteer alinea's
        qs = RJAlinea.objects.select_related("sectie__hoofdstuk")
        if not force:
            qs = qs.filter(embedding__isnull=True)

        alineas = list(qs)
        if not alineas:
            self.stdout.write("Geen alinea's om te embedden.")
            return

        self.stdout.write(f"Model laden: {model_name}...")
        model = SentenceTransformer(model_name)

        self.stdout.write(f"Embeddings genereren voor {len(alineas)} alinea's...")

        # Bouw teksten met context voor betere embeddings
        texts = []
        for a in alineas:
            # Voeg context toe: hoofdstuk + sectie + sub_onderwerp + inhoud
            parts = [
                f"RJ {a.sectie.hoofdstuk.code}: {a.sectie.hoofdstuk.titel}",
                f"§ {a.sectie.paragraaf}: {a.sectie.titel}",
            ]
            if a.sub_onderwerp:
                parts.append(f"Onderwerp: {a.sub_onderwerp}")
            parts.append(a.inhoud[:2000])  # Beperk lengte voor embedding model
            texts.append(" | ".join(parts))

        # Genereer embeddings in batches
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        # Sla op in database
        for alinea, emb in zip(alineas, embeddings):
            alinea.embedding = emb.tolist()

        RJAlinea.objects.bulk_update(alineas, ["embedding"], batch_size=100)

        self.stdout.write(
            self.style.SUCCESS(f"Klaar: {len(alineas)} embeddings opgeslagen")
        )
