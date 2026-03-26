"""
Generiek OCR command — converteert een PDF naar markdown via Mistral OCR API.

Verwerkt pagina voor pagina en slaat het resultaat op als .md bestand.
Herbruikbaar voor elk PDF-document (boeken, richtlijnen, etc.).
"""

import base64
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Converteer een PDF naar markdown via Mistral OCR"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            help="Pad naar het PDF-bestand",
        )
        parser.add_argument(
            "--output",
            required=True,
            help="Pad voor het output markdown-bestand",
        )
        parser.add_argument(
            "--start-page",
            type=int,
            default=1,
            help="Startpagina (1-based, standaard 1)",
        )
        parser.add_argument(
            "--end-page",
            type=int,
            default=0,
            help="Eindpagina (0 = alle pagina's, standaard 0)",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=50,
            help="Aantal pagina's per API-aanroep (standaard 50, max verschilt per PDF grootte)",
        )
        parser.add_argument(
            "--resume",
            action="store_true",
            help="Ga verder waar eerder gestopt (append aan bestaand bestand)",
        )

    def handle(self, *args, **options):
        pdf_path = options["file"]
        output_path = options["output"]
        chunk_size = options["chunk_size"]
        resume = options["resume"]

        if not os.path.isfile(pdf_path):
            self.stderr.write(self.style.ERROR(f"Bestand niet gevonden: {pdf_path}"))
            return

        api_key = os.environ.get("MISTRAL_API_KEY", "")
        if not api_key:
            self.stderr.write(self.style.ERROR("MISTRAL_API_KEY is niet ingesteld in .env"))
            return

        try:
            from mistralai import Mistral
        except ImportError:
            try:
                from mistralai.client import Mistral
            except ImportError:
                self.stderr.write(self.style.ERROR("pip install mistralai"))
                return

        # Bepaal totaal aantal pagina's via PyMuPDF (als beschikbaar) of schat
        total_pages = self._count_pages(pdf_path)
        if total_pages:
            self.stdout.write(f"PDF heeft {total_pages} pagina's")

        start_page = options["start_page"]
        end_page = options["end_page"] or total_pages or 9999

        # Bepaal startpunt bij resume
        if resume and os.path.isfile(output_path):
            last_page = self._find_last_page(output_path)
            if last_page:
                start_page = last_page + 1
                self.stdout.write(f"Hervat vanaf pagina {start_page}")

        client = Mistral(api_key=api_key, timeout_ms=300_000)

        # Verwerk in chunks om geheugen en API-limieten te beheren
        mode = "a" if resume else "w"
        with open(output_path, mode, encoding="utf-8") as out_f:
            if not resume:
                out_f.write(f"# OCR Output: {os.path.basename(pdf_path)}\n\n")

            page_num = start_page
            while page_num <= end_page:
                chunk_end = min(page_num + chunk_size - 1, end_page)
                self.stdout.write(f"Verwerken pagina's {page_num}-{chunk_end}...")

                try:
                    pdf_bytes = self._extract_pages(pdf_path, page_num, chunk_end)
                    if not pdf_bytes:
                        self.stdout.write("Geen pagina's meer — klaar.")
                        break

                    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

                    ocr_response = client.ocr.process(
                        model="mistral-ocr-latest",
                        document={
                            "type": "document_url",
                            "document_url": f"data:application/pdf;base64,{pdf_base64}",
                        },
                    )

                    for i, page in enumerate(ocr_response.pages):
                        actual_page = page_num + i
                        out_f.write(f"\n\n--- Pagina {actual_page} ---\n\n")
                        out_f.write(page.markdown)
                    out_f.flush()

                    processed = len(ocr_response.pages)
                    self.stdout.write(
                        self.style.SUCCESS(f"  OK: {processed} pagina's verwerkt")
                    )

                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"  Fout bij pagina's {page_num}-{chunk_end}: {e}")
                    )
                    self.stdout.write(f"  Hervat later met --resume --start-page {page_num}")
                    break

                page_num = chunk_end + 1

        self.stdout.write(self.style.SUCCESS(f"Output opgeslagen: {output_path}"))

    def _count_pages(self, pdf_path):
        """Tel pagina's via PyMuPDF (optioneel)."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except ImportError:
            return None

    def _extract_pages(self, pdf_path, start, end):
        """Extraheer een range pagina's als losse PDF bytes."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            if start - 1 >= len(doc):
                doc.close()
                return None
            end = min(end, len(doc))
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start - 1, to_page=end - 1)
            pdf_bytes = new_doc.tobytes()
            new_doc.close()
            doc.close()
            return pdf_bytes
        except ImportError:
            # Fallback: stuur hele PDF (werkt alleen voor kleine bestanden)
            if start > 1:
                self.stderr.write(
                    "PyMuPDF niet geïnstalleerd — kan geen pagina-range extraheren. "
                    "pip install pymupdf"
                )
                return None
            with open(pdf_path, "rb") as f:
                return f.read()

    def _find_last_page(self, output_path):
        """Zoek het laatste paginanummer in een bestaand output bestand."""
        import re
        last_page = None
        pattern = re.compile(r"--- Pagina (\d+) ---")
        with open(output_path, "r", encoding="utf-8") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    last_page = int(m.group(1))
        return last_page
