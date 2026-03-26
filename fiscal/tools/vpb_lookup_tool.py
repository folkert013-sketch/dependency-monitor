"""
VPB Wet Lookup Tool voor CrewAI.

Geeft agents toegang tot officiële fiscale wetsartikelen
(Wet Vpb 1969 en gerelateerde wetten).
"""

from crewai.tools import BaseTool


class VpbLookupTool(BaseTool):
    name: str = "vpb_wet_lookup"
    description: str = (
        "Zoekt officiële wetsartikelen uit de Wet op de Vennootschapsbelasting 1969 "
        "en gerelateerde fiscale wetten op. "
        "Input: een wetsartikel (bijv. 'art. 13 Vpb', 'artikel 20 lid 2'), "
        "een fiscaal concept (bijv. 'deelnemingsvrijstelling', 'verliesverrekening', "
        "'fiscale eenheid', 'innovatiebox'), of een inhoudelijke vraag. "
        "Optioneel boekjaar meegeven met '| jaar' (bijv. 'art. 13 | 2025'). "
        "Returns: relevante wetsartikelen met artikelnummer, titel en volledige tekst."
    )

    def _run(self, query: str = "") -> str:
        from dashboard.services.vpb_knowledge import VpbKnowledgeService

        query = query.strip()
        if not query:
            return (
                "Geef een zoekopdracht op. Voorbeelden:\n"
                "- 'art. 13 Vpb' voor de deelnemingsvrijstelling\n"
                "- 'artikel 20 lid 2' voor verliesverrekening\n"
                "- 'deelnemingsvrijstelling' voor concept-lookup\n"
                "- 'renteaftrekbeperking' voor semantisch zoeken"
            )

        service = VpbKnowledgeService()
        result = service.combined_lookup(query)

        if len(result) > 8000:
            result = result[:8000] + "\n\n*[Resultaat ingekort — gebruik een specifiekere zoekopdracht]*"

        return result
