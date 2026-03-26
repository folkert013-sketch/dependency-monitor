"""
RJ Richtlijnen Lookup Tool voor CrewAI.

Geeft agents toegang tot de Richtlijnen voor de Jaarverslaggeving
voor micro- en kleine rechtspersonen.
"""

from crewai.tools import BaseTool


class RJLookupTool(BaseTool):
    name: str = "rj_richtlijnen_lookup"
    description: str = (
        "Zoekt specifieke Richtlijnen voor de Jaarverslaggeving (RJ) op "
        "voor micro- en kleine rechtspersonen. "
        "Input: een RJ-code (bijv. 'B2', 'B2.1', 'B2.1.101'), "
        "een jaarrekening-rubriek (bijv. 'materiële vaste activa', 'voorraden', "
        "'voorzieningen', 'eigen vermogen'), of een inhoudelijke vraag "
        "(bijv. 'hoe waardeer ik voorraden', 'afschrijving levensduur'). "
        "Returns: relevante RJ-alinea's met referentienummer, titel en volledige inhoud."
    )

    def _run(self, query: str = "") -> str:
        from dashboard.services.rj_knowledge import RJKnowledgeService

        query = query.strip()
        if not query:
            return (
                "Geef een zoekopdracht op. Voorbeelden:\n"
                "- 'B2' voor hoofdstuk Materiële vaste activa\n"
                "- 'B4.1.103' voor een specifieke alinea over voorraden\n"
                "- 'voorraden' voor de rubriek Voorraden\n"
                "- 'hoe waardeer ik immateriële activa' voor semantisch zoeken"
            )

        service = RJKnowledgeService()
        result = service.combined_lookup(query)

        # Beperk output lengte voor LLM context
        if len(result) > 8000:
            result = result[:8000] + "\n\n*[Resultaat ingekort — gebruik een specifiekere zoekopdracht]*"

        return result
