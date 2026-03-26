"""
IB Wet Lookup Tool — zoekt wetsartikelen uit de Wet IB 2001 op.
"""

from crewai.tools import BaseTool

_MAX_RESULT_LEN = 8000


class IbLookupTool(BaseTool):
    name: str = "ib_lookup"
    description: str = (
        "Zoekt officiële wetsartikelen uit de Wet inkomstenbelasting 2001 op. "
        "Ondersteunt artikelnummers (bijv. 'art. 3.1 IB', 'artikel 4.12 lid 2'), "
        "fiscale concepten (bijv. 'box 2', 'zelfstandigenaftrek', 'heffingskorting') "
        "en inhoudelijke vragen. Optioneel boekjaar meegeven: 'art. 3.1 | 2025'. "
        "Retourneert de relevante wettekst."
    )

    def _run(self, query: str = "") -> str:
        if not query or not query.strip():
            return (
                "Geef een wetsartikel (bijv. 'art. 3.1 IB'), "
                "een concept (bijv. 'box 2') of een vraag op."
            )

        from dashboard.services.ib_knowledge import IbKnowledgeService

        service = IbKnowledgeService()
        result = service.combined_lookup(query)

        if len(result) > _MAX_RESULT_LEN:
            result = result[:_MAX_RESULT_LEN] + "\n\n[... afgekapt]"
        return result
