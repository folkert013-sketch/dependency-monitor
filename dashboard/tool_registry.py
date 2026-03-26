"""
Registry of all available tools that can be assigned to Team agents.
Each entry maps a string identifier to a label, description, and factory.
"""

from monitor.tools import (
    APIStatusCheckerTool,
    EmailSenderTool,
    GitHubChangelogTool,
    MistralOCRTool,
    PyPIVersionCheckerTool,
    RequirementsReaderTool,
    VulnerabilityScannerTool,
)
from fiscal.tools import (
    ArticleContentExtractorTool,
    BelastingdienstStructuredDataTool,
    FiscalDeadlineCheckerTool,
    FiscalNewsAggregatorTool,
    GovernmentSiteFetcherTool,
    TaxNewsSearcherTool,
    DutchTaxRateComparatorTool,
    VpbLookupTool,
    VpbBoekLookupTool,
    VpbTarievenTool,
    IbLookupTool,
    IbTarievenTool,
)
from compliance.tools import (
    AdverseMediaSearcherTool,
    PEPScreenerTool,
    SanctionsCheckerTool,
    WWFTLegislationFetcherTool,
)
from samenstellen.tools import RJLookupTool, MarkdownToPDFTool

TOOL_REGISTRY = {
    # --- Dependency Monitor ---
    "requirements_reader": {
        "label": "Requirements Reader",
        "description": "Leest en parset requirements.txt",
        "category": "monitor",
        "cls": RequirementsReaderTool,
    },
    "pypi_checker": {
        "label": "PyPI Version Checker",
        "description": "Checkt nieuwste versie op PyPI",
        "category": "monitor",
        "cls": PyPIVersionCheckerTool,
    },
    "api_status_checker": {
        "label": "API Status Checker",
        "description": "Checkt status van gemonitorde API's",
        "category": "monitor",
        "cls": APIStatusCheckerTool,
    },
    "vuln_scanner": {
        "label": "Vulnerability Scanner",
        "description": "Scant tegen OSV.dev kwetsbaarheidsdb",
        "category": "monitor",
        "cls": VulnerabilityScannerTool,
    },
    "github_changelog": {
        "label": "GitHub Changelog",
        "description": "Haalt GitHub release notes op",
        "category": "monitor",
        "cls": GitHubChangelogTool,
    },
    "email_sender": {
        "label": "Email Sender",
        "description": "Verstuurt e-mails (MS Graph API)",
        "category": "monitor",
        "cls": EmailSenderTool,
    },
    "mistral_ocr": {
        "label": "Mistral OCR (PDF->Tekst)",
        "description": "Verwerkt PDF-documenten met Mistral OCR en retourneert tekst als markdown",
        "category": "fiscal",
        "cls": MistralOCRTool,
    },
    # --- Fiscale Monitor ---
    "gov_site_fetcher": {
        "label": "Government Site Fetcher",
        "description": "Fetcht Nederlandse overheidssites",
        "category": "fiscal",
        "cls": GovernmentSiteFetcherTool,
    },
    "tax_news_searcher": {
        "label": "Tax News Searcher",
        "description": "Zoekt fiscaal nieuws en ontwikkelingen",
        "category": "fiscal",
        "cls": TaxNewsSearcherTool,
    },
    "deadline_checker": {
        "label": "Fiscal Deadline Checker",
        "description": "Controleert fiscale deadlines",
        "category": "fiscal",
        "cls": FiscalDeadlineCheckerTool,
    },
    "article_content_extractor": {
        "label": "Article Content Extractor",
        "description": "Haalt artikelinhoud op van URLs (overheid + nieuws + vakbladen)",
        "category": "fiscal",
        "cls": ArticleContentExtractorTool,
    },
    "tax_rate_comparator": {
        "label": "Dutch Tax Rate Comparator",
        "description": "Vergelijkt belastingtarieven 2025 vs 2026",
        "category": "fiscal",
        "cls": DutchTaxRateComparatorTool,
    },
    "fiscal_news_aggregator": {
        "label": "Fiscal News Aggregator",
        "description": "Doorzoekt vakbladen, nieuws en MKB-bronnen",
        "category": "fiscal",
        "cls": FiscalNewsAggregatorTool,
    },
    "belastingdienst_data": {
        "label": "Belastingdienst Structured Data",
        "description": "Haalt gestructureerde tarieven/tabellen van belastingdienst.nl",
        "category": "fiscal",
        "cls": BelastingdienstStructuredDataTool,
    },
    # --- VPB Fiscale Wetgeving ---
    "vpb_lookup": {
        "label": "VPB Wet Lookup",
        "description": "Zoekt officiële wetsartikelen Vpb 1969 op (artikel, concept of vraag)",
        "category": "fiscal",
        "cls": VpbLookupTool,
    },
    "vpb_boek_lookup": {
        "label": "VPB Boek Lookup (Wegwijs)",
        "description": "Zoekt in 'Wegwijs in de Vennootschapsbelasting' — praktische uitleg en voorbeelden",
        "category": "fiscal",
        "cls": VpbBoekLookupTool,
    },
    "vpb_tarieven": {
        "label": "VPB Tarievenlijst",
        "description": "Zoekt VPB-tarieven en drempels op per boekjaar (bijv. 'tarief | 2023')",
        "category": "fiscal",
        "cls": VpbTarievenTool,
    },
    # --- IB (Inkomstenbelasting) ---
    "ib_lookup": {
        "label": "IB Wet Lookup",
        "description": "Zoekt officiële wetsartikelen Wet IB 2001 op (artikel, concept of vraag)",
        "category": "fiscal",
        "cls": IbLookupTool,
    },
    "ib_tarieven": {
        "label": "IB Tarievenlijst",
        "description": "Zoekt IB-tarieven en drempels op per boekjaar (bijv. 'box 1 | 2023')",
        "category": "fiscal",
        "cls": IbTarievenTool,
    },
    # --- WWFT Compliance ---
    "sanctions_checker": {
        "label": "Sanctions Checker",
        "description": "Doorzoekt EU/NL/VN sanctielijsten",
        "category": "compliance",
        "cls": SanctionsCheckerTool,
    },
    "pep_screener": {
        "label": "PEP Screener",
        "description": "Screent op Politically Exposed Persons",
        "category": "compliance",
        "cls": PEPScreenerTool,
    },
    "wwft_legislation_fetcher": {
        "label": "WWFT Legislation Fetcher",
        "description": "Haalt actuele WWFT wet- en regelgeving op",
        "category": "compliance",
        "cls": WWFTLegislationFetcherTool,
    },
    "adverse_media_searcher": {
        "label": "Adverse Media Searcher",
        "description": "Doorzoekt nieuwsbronnen op negatieve berichtgeving",
        "category": "compliance",
        "cls": AdverseMediaSearcherTool,
    },
    # --- Samenstelopdracht / Verslaggeving ---
    "rj_lookup": {
        "label": "RJ Richtlijnen Lookup",
        "description": "Zoekt RJ-richtlijnen op (code, rubriek of inhoudelijke vraag)",
        "category": "samenstellen",
        "cls": RJLookupTool,
    },
    "markdown_to_pdf": {
        "label": "Markdown naar PDF",
        "description": "Converteert markdown-tekst naar professioneel PDF-rapport",
        "category": "samenstellen",
        "cls": MarkdownToPDFTool,
    },
}

TOOL_CATEGORY_LABELS = {
    "monitor": "Dependency Monitor",
    "fiscal": "Fiscale Monitor",
    "compliance": "WWFT Compliance",
    "samenstellen": "Samenstelopdracht / Verslaggeving",
}


def get_tools_by_category():
    """Return tools grouped by category."""
    categories = {}
    for tid, entry in TOOL_REGISTRY.items():
        cat = entry.get("category", "monitor")
        if cat not in categories:
            categories[cat] = {"label": TOOL_CATEGORY_LABELS.get(cat, cat), "tools": []}
        categories[cat]["tools"].append({"id": tid, "label": entry["label"], "description": entry["description"]})
    return categories


def get_tool_choices():
    """Return a list of (identifier, label) tuples for form selects."""
    return [(k, v["label"]) for k, v in TOOL_REGISTRY.items()]


def instantiate_tools(tool_ids: list, **kwargs) -> list:
    """Create tool instances for a list of tool identifiers."""
    tools = []
    for tid in tool_ids:
        entry = TOOL_REGISTRY.get(tid)
        if not entry:
            continue
        cls = entry["cls"]
        # Some tools accept init kwargs (e.g. requirements_path, config_path)
        try:
            tools.append(cls(**kwargs))
        except TypeError:
            tools.append(cls())
    return tools
