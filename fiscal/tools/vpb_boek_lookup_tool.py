"""
VPB Boek Lookup Tool voor CrewAI.

Geeft agents toegang tot 'Wegwijs in de Vennootschapsbelasting' (18e druk 2023)
— praktische uitleg, voorbeelden en interpretatie van VPB-onderwerpen.
"""

from crewai.tools import BaseTool


class VpbBoekLookupTool(BaseTool):
    name: str = "vpb_boek_lookup"
    description: str = (
        "Zoekt in het boek 'Wegwijs in de Vennootschapsbelasting'. "
        "Bevat praktische uitleg, rekenvoorbeelden en interpretatie van VPB-onderwerpen. "
        "Input: een fiscaal onderwerp (bijv. 'deelnemingsvrijstelling', 'innovatiebox'). "
        "Optioneel editie meegeven met '| jaar' (bijv. 'deelnemingsvrijstelling | 2025'). "
        "Returns: relevante passages met hoofdstuk, sectie en paginanummer."
    )

    def _run(self, query: str = "") -> str:
        from dashboard.services.vpb_boek_knowledge import VpbBoekKnowledgeService

        query = query.strip()
        if not query:
            return (
                "Geef een onderwerp op. Voorbeelden:\n"
                "- 'deelnemingsvrijstelling'\n"
                "- 'innovatiebox'\n"
                "- 'fiscale eenheid vormen'\n"
                "- 'verliesverrekening termijnen'"
            )

        service = VpbBoekKnowledgeService()
        result = service.combined_lookup(query)

        if len(result) > 8000:
            result = result[:8000] + "\n\n*[Resultaat ingekort — gebruik een specifiekere zoekopdracht]*"

        return result
