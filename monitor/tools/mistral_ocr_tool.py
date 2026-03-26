"""
Mistral OCR Tool — Verwerkt PDF-documenten via de Mistral OCR API
en retourneert de volledige tekst als markdown.
"""

import base64
import os

from crewai.tools import BaseTool


class MistralOCRTool(BaseTool):
    name: str = "Mistral OCR"
    description: str = (
        "Verwerkt een PDF-document met Mistral OCR en retourneert "
        "de volledige tekst als markdown. Geef het pad naar een PDF-bestand."
    )

    def _run(self, pdf_path: str = "") -> str:
        api_key = os.environ.get("MISTRAL_API_KEY", "")
        if not api_key:
            return "FOUT: MISTRAL_API_KEY is niet ingesteld in .env. Kan de OCR niet uitvoeren."

        pdf_path = pdf_path.strip()
        if not pdf_path or not os.path.isfile(pdf_path):
            return f"FOUT: Bestand niet gevonden: {pdf_path}. Controleer het pad."

        # Bestandsgrootte-check: max 20 MB
        max_size = 20 * 1024 * 1024
        file_size = os.path.getsize(pdf_path)
        if file_size > max_size:
            return f"FOUT: Bestand te groot ({file_size // (1024 * 1024)}MB, max 20MB)."

        try:
            from mistralai.client import Mistral
        except ImportError:
            try:
                from mistralai import Mistral
            except ImportError:
                return "FOUT: mistralai package niet geïnstalleerd. Voer uit: pip install mistralai"

        client = Mistral(api_key=api_key, timeout_ms=120_000)

        with open(pdf_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{pdf_base64}",
            },
        )

        pages = []
        for i, page in enumerate(ocr_response.pages):
            pages.append(f"--- Pagina {i + 1} ---\n{page.markdown}")

        return "\n\n".join(pages) if pages else "Geen tekst gevonden in het document."
