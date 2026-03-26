"""
Markdown naar PDF Tool — Converteert markdown-tekst naar een professioneel
opgemaakt PDF-rapport met FenoFin huisstijl.
"""

import os
import re
from datetime import datetime
from pathlib import Path

from crewai.tools import BaseTool


# Project root: samenstellen/tools/ → twee niveaus omhoog
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_REPORTS_DIR = _PROJECT_ROOT / "media" / "reports"

PDF_STYLES = """
@page {
    size: A4;
    margin: 2.5cm 2.5cm 3cm 2.5cm;
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-size: 9px;
        color: #999;
    }
}
body {
    font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
    font-size: 11pt;
    color: #1a1a2e;
    line-height: 1.7;
}
.header {
    border-bottom: 3px solid #4338ca;
    padding-bottom: 14px;
    margin-bottom: 30px;
}
.header h1 {
    font-size: 22pt;
    color: #312e81;
    margin: 0 0 6px 0;
    letter-spacing: -0.3px;
}
.header .meta {
    font-size: 9pt;
    color: #6b7280;
}
.content h1 {
    font-size: 16pt;
    color: #312e81;
    border-bottom: 2px solid #e0e7ff;
    padding-bottom: 6px;
    margin-top: 24px;
    page-break-before: always;
}
.content h1:first-child {
    page-break-before: avoid;
}
.content h2 {
    font-size: 13pt;
    color: #4338ca;
    margin-top: 28px;
    border-bottom: 1px solid #e0e7ff;
    padding-bottom: 4px;
    page-break-after: avoid;
}
.content h3 {
    font-size: 11pt;
    color: #475569;
    margin-top: 14px;
    page-break-after: avoid;
}
.content p {
    margin: 6px 0;
    orphans: 3;
    widows: 3;
}
.content ul, .content ol {
    padding-left: 22px;
    margin: 6px 0;
    page-break-before: avoid;
}
.content li {
    margin: 3px 0;
    orphans: 3;
    widows: 3;
}
.content blockquote {
    border-left: 3px solid #c7d2fe;
    background: #f5f3ff;
    padding: 10px 16px;
    margin: 12px 0;
    font-style: italic;
    color: #4338ca;
    page-break-inside: avoid;
}
.content hr {
    border: none;
    border-top: 1px solid #e0e7ff;
    margin: 24px 0;
}
.content table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 10pt;
    page-break-inside: avoid;
}
.content th {
    background: #f1f5f9;
    font-weight: 600;
    border-bottom: 2px solid #e2e8f0;
    padding: 7px 10px;
    text-align: left;
}
.content td {
    padding: 6px 10px;
    border-bottom: 1px solid #f1f5f9;
}
.content code {
    background: #f1f5f9;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 9pt;
}
.content pre {
    background: #f8fafc;
    padding: 12px;
    border-radius: 6px;
    font-size: 9pt;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}
"""


def _pdf_safe_text(text):
    """Replace emoji characters with text equivalents for PDF rendering."""
    return (
        text
        .replace("\u2705", "[OK]")          # ✅
        .replace("\u274c", "[FOUT]")        # ❌
        .replace("\u26a0\ufe0f", "[LET OP]")  # ⚠️
        .replace("\u26a0", "[LET OP]")      # ⚠
        .replace("\u2713", "[OK]")          # ✓
        .replace("\u2717", "[FOUT]")        # ✗
        .replace("\u2714", "[OK]")          # ✔
        .replace("\u2718", "[FOUT]")        # ✘
    )


def _extract_title(markdown_text):
    """Extract the first H1 heading from markdown, or return default."""
    match = re.search(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
    return match.group(1).strip() if match else "Rapport"


def _slugify(text):
    """Simple slug from text for filename."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:50]


class MarkdownToPDFTool(BaseTool):
    name: str = "markdown_to_pdf"
    description: str = (
        "Converteert markdown-tekst naar een professioneel opgemaakt PDF-rapport. "
        "Geef de volledige markdown-inhoud als input. De titel wordt automatisch "
        "afgeleid uit het eerste H1-kopje. Retourneert het pad naar het "
        "gegenereerde PDF-bestand."
    )

    def _run(self, markdown_content: str = "") -> str:
        if not markdown_content or not markdown_content.strip():
            return "FOUT: Geen markdown-inhoud opgegeven. Geef de tekst die je naar PDF wilt converteren."

        try:
            import markdown2
        except ImportError:
            return "FOUT: markdown2 package niet geinstalleerd. Voer uit: pip install markdown2"

        try:
            import weasyprint
        except ImportError:
            return "FOUT: weasyprint package niet geinstalleerd. Voer uit: pip install weasyprint"

        title = _extract_title(markdown_content)
        safe_text = _pdf_safe_text(markdown_content)

        html_body = markdown2.markdown(
            safe_text,
            extras=[
                "fenced-code-blocks",
                "tables",
                "header-ids",
                "strike",
                "task_list",
                "cuddled-lists",
            ],
        )

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        date_display = now.strftime("%d-%m-%Y %H:%M")

        html_content = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{PDF_STYLES}</style>
</head><body>
    <div class="header">
        <h1>{title}</h1>
        <div class="meta">Rapport gegenereerd op {date_display}</div>
    </div>
    <div class="content">{html_body}</div>
</body></html>"""

        os.makedirs(_REPORTS_DIR, exist_ok=True)
        slug = _slugify(title)
        filename = f"{slug}_{timestamp}.pdf"
        output_path = _REPORTS_DIR / filename

        try:
            pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
        except Exception as e:
            return f"FOUT: PDF generatie mislukt: {e}"

        return f"PDF-rapport gegenereerd: {output_path}"
