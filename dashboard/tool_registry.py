"""
Registry of all available tools that can be assigned to Team agents.
Each entry maps a string identifier to a label, description, and factory.
"""

from monitor.tools import (
    APIStatusCheckerTool,
    EmailSenderTool,
    GitHubChangelogTool,
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
)
from compliance.tools import (
    AdverseMediaSearcherTool,
    PEPScreenerTool,
    SanctionsCheckerTool,
    WWFTLegislationFetcherTool,
)

TOOL_REGISTRY = {
    "requirements_reader": {
        "label": "Requirements Reader",
        "description": "Leest en parset requirements.txt",
        "cls": RequirementsReaderTool,
    },
    "pypi_checker": {
        "label": "PyPI Version Checker",
        "description": "Checkt nieuwste versie op PyPI",
        "cls": PyPIVersionCheckerTool,
    },
    "api_status_checker": {
        "label": "API Status Checker",
        "description": "Checkt status van gemonitorde API's",
        "cls": APIStatusCheckerTool,
    },
    "vuln_scanner": {
        "label": "Vulnerability Scanner",
        "description": "Scant tegen OSV.dev kwetsbaarheidsdb",
        "cls": VulnerabilityScannerTool,
    },
    "github_changelog": {
        "label": "GitHub Changelog",
        "description": "Haalt GitHub release notes op",
        "cls": GitHubChangelogTool,
    },
    "email_sender": {
        "label": "Email Sender",
        "description": "Verstuurt e-mails (SMTP)",
        "cls": EmailSenderTool,
    },
    "gov_site_fetcher": {
        "label": "Government Site Fetcher",
        "description": "Fetcht Nederlandse overheidssites",
        "cls": GovernmentSiteFetcherTool,
    },
    "tax_news_searcher": {
        "label": "Tax News Searcher",
        "description": "Zoekt fiscaal nieuws en ontwikkelingen",
        "cls": TaxNewsSearcherTool,
    },
    "deadline_checker": {
        "label": "Fiscal Deadline Checker",
        "description": "Controleert fiscale deadlines",
        "cls": FiscalDeadlineCheckerTool,
    },
    "article_content_extractor": {
        "label": "Article Content Extractor",
        "description": "Haalt artikelinhoud op van URLs (overheid + nieuws + vakbladen)",
        "cls": ArticleContentExtractorTool,
    },
    "tax_rate_comparator": {
        "label": "Dutch Tax Rate Comparator",
        "description": "Vergelijkt belastingtarieven 2025 vs 2026",
        "cls": DutchTaxRateComparatorTool,
    },
    "fiscal_news_aggregator": {
        "label": "Fiscal News Aggregator",
        "description": "Doorzoekt vakbladen, nieuws en MKB-bronnen",
        "cls": FiscalNewsAggregatorTool,
    },
    "belastingdienst_data": {
        "label": "Belastingdienst Structured Data",
        "description": "Haalt gestructureerde tarieven/tabellen van belastingdienst.nl",
        "cls": BelastingdienstStructuredDataTool,
    },
    "sanctions_checker": {
        "label": "Sanctions Checker",
        "description": "Doorzoekt EU/NL/VN sanctielijsten",
        "cls": SanctionsCheckerTool,
    },
    "pep_screener": {
        "label": "PEP Screener",
        "description": "Screent op Politically Exposed Persons",
        "cls": PEPScreenerTool,
    },
    "wwft_legislation_fetcher": {
        "label": "WWFT Legislation Fetcher",
        "description": "Haalt actuele WWFT wet- en regelgeving op",
        "cls": WWFTLegislationFetcherTool,
    },
    "adverse_media_searcher": {
        "label": "Adverse Media Searcher",
        "description": "Doorzoekt nieuwsbronnen op negatieve berichtgeving",
        "cls": AdverseMediaSearcherTool,
    },
}


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
