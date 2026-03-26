"""Seed het VPB Fiscale Review team met hiërarchisch process."""

from django.db import migrations

# De werkelijke secties van het VPB-aangifteformulier (Belastingdienst)
VPB_SECTIES = """
1. Belastingplichtige — basisgegevens, rechtsvorm, boekjaar, hoofdactiviteiten, fiscaal ondernemingsvermogen
2. Investeringen — investeringsaftrek, desinvesteringsbijtelling
3. Deelnemingen en deelnemingsvrijstelling — belang, balansgarantie, afgewaardeerde vorderingen
4. Balans: Activa — financiële vaste activa, vorderingen, liquide middelen
5. Balans: Passiva — ondernemingsvermogen, gestort kapitaal, winstreserves, schulden
6. Winst-en-verliesrekening — bedrijfskosten, financiële baten/lasten, resultaat
7. Aandeelhouders — aanmerkelijk belang, aandelenbezit, schulden/vorderingen, informeel kapitaal
8. Deelnemingen (detail) — per deelneming: percentage, opgeofferd bedrag, balanswaardering, nettovoordelen
9. Fiscale winst — vermogensvergelijking (begin/einde boekjaar)
10. Houdsteractiviteiten en dergelijke — houdstermaatschappij, internationale activiteiten
11. Renteaftrekbeperking — earningsstripping, specifieke renteaftrekbeperkingen
12. Overzicht belastbare winst — saldo fiscale winstberekening, deelnemingsvrijstelling, belastbaar bedrag
13. Verliesverrekening — carry-back, carry-forward, restant verlies
14. Overzicht belastingbedrag — tarief, schijven, berekening, te betalen bedrag
""".strip()


def seed_vpb_review_team(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamVariable = apps.get_model("dashboard", "TeamVariable")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")
    User = apps.get_model("auth", "User")

    owner = User.objects.filter(is_superuser=True).first()

    team = Team.objects.filter(slug="vpb-fiscale-review").first()
    if not team:
        team = Team.objects.create(
            name="VPB Fiscale Review",
            slug="vpb-fiscale-review",
            description=(
                "Reviewt een VPB-aangifte per sectie aan de hand van "
                "officiële wetsartikelen (Wet Vpb 1969) én het vakboek 'Wegwijs in de "
                "Vennootschapsbelasting'. Levert een PDF-rapport met bevindingen, "
                "risico's en fiscale optimalisatiekansen."
            ),
            process="hierarchical",
            verbose=True,
            owner=owner,
        )

    # Opschonen
    team.agents.all().delete()
    team.variables.all().delete()

    # --- Variabelen ---
    TeamVariable.objects.create(
        team=team,
        name="document_path",
        label="VPB-aangifte PDF",
        description="Upload de VPB-aangifte als PDF-bestand.",
        input_type="file_path",
        default_value="",
        required=True,
        order=0,
    )
    TeamVariable.objects.create(
        team=team,
        name="jaarrekening_path",
        label="Jaarrekening PDF",
        description="Optioneel: upload de commerciele jaarrekening ter vergelijking.",
        input_type="file_path",
        default_value="",
        required=False,
        order=1,
    )
    TeamVariable.objects.create(
        team=team,
        name="extra_document_path",
        label="Extra document PDF",
        description="Optioneel: upload een extra document, bijv. een memo, leningsovereenkomst of notulen.",
        input_type="file_path",
        default_value="",
        required=False,
        order=2,
    )
    TeamVariable.objects.create(
        team=team,
        name="klant_bijzonderheden",
        label="Bijzonderheden klant",
        description=(
            "Bijzonderheden die relevant zijn voor de review, bijv.: "
            "'Client is in 2025 geliquideerd', 'Fiscale eenheid verbroken per 1-1-2024', "
            "'Deelneming verkocht in Q3', 'Eerste jaar BV', 'DGA pensioen afgekocht', etc."
        ),
        input_type="textarea",
        default_value="",
        required=False,
        order=3,
    )

    # --- Agent 0: OCR Specialist ---
    ocr_agent = TeamAgent.objects.create(
        team=team,
        order=0,
        role="VPB-aangifte OCR Specialist",
        goal=(
            "Lees de volgende documenten in via OCR en lever de volledige "
            "tekst op als gestructureerde markdown:\n\n"
            "1. VPB-aangifte (verplicht): '{document_path}'\n"
            "2. Jaarrekening (indien aanwezig): '{jaarrekening_path}'\n"
            "3. Extra document (indien aanwezig): '{extra_document_path}'\n\n"
            "Markeer duidelijk per document welke informatie eruit komt. "
            "Identificeer in de VPB-aangifte de volgende secties:\n" + VPB_SECTIES
        ),
        backstory=(
            "Je bent een documentspecialist getraind in het verwerken van "
            "VPB-aangiften van de Belastingdienst. Je herkent de structuur "
            "van het aangifteformulier feilloos."
        ),
        llm_provider="gemini",
        llm_model="gemini-3-flash-preview",
        tools=["mistral_ocr"],
        max_iter=10,
        verbose=True,
    )

    # --- Agent 1: VPB Wet Specialist ---
    wet_agent = TeamAgent.objects.create(
        team=team,
        order=1,
        role="VPB Wet Specialist",
        goal=(
            "Toets de VPB-aangifte per sectie aan de officiële wetsartikelen uit "
            "de Wet op de Vennootschapsbelasting 1969. Gebruik de vpb_wet_lookup "
            "tool om per sectie de relevante artikelen op te zoeken. Controleer "
            "of de aangifte conform de wet is en rapporteer afwijkingen met "
            "exacte artikelverwijzingen.\n\n"
            "Bijzonderheden klant (geef hier extra aandacht aan): {klant_bijzonderheden}"
        ),
        backstory=(
            "Je bent een fiscaal jurist gespecialiseerd in de "
            "vennootschapsbelasting. Je kent de Wet Vpb 1969 door en door "
            "en toetst methodisch elke post in de aangifte aan de wet."
        ),
        llm_provider="gemini",
        llm_model="gemini-3-flash-preview",
        tools=["vpb_lookup"],
        max_iter=40,
        verbose=True,
    )

    # --- Agent 2: VPB Boek Specialist ---
    boek_agent = TeamAgent.objects.create(
        team=team,
        order=2,
        role="VPB Boek Specialist",
        goal=(
            "Zoek per sectie van de VPB-aangifte de praktische uitleg, "
            "voorbeelden en aandachtspunten op in 'Wegwijs in de "
            "Vennootschapsbelasting'. Geef context bij de wettelijke regels.\n\n"
            "Bijzonderheden klant (zoek hier specifiek passages over): {klant_bijzonderheden}"
        ),
        backstory=(
            "Je bent een ervaren belastingadviseur die het standaardwerk "
            "'Wegwijs in de Vennootschapsbelasting' van buiten kent. Je "
            "vertaalt droge wetteksten naar praktische inzichten."
        ),
        llm_provider="gemini",
        llm_model="gemini-3-flash-preview",
        tools=["vpb_boek_lookup"],
        max_iter=40,
        verbose=True,
    )

    # --- Agent 3: Fiscaal Advies Specialist ---
    advies_agent = TeamAgent.objects.create(
        team=team,
        order=3,
        role="Fiscaal Advies Specialist",
        goal=(
            "Analyseer de VPB-aangifte op fiscale optimalisatiemogelijkheden. "
            "Gebruik zowel de wetteksten als het vakboek om per sectie te "
            "identificeren: gemiste aftrekposten, optimalisatiemogelijkheden, "
            "en fiscale faciliteiten. Onderbouw elk advies met wetsartikelen "
            "en praktische toelichting.\n\n"
            "Bijzonderheden klant (specifieke kansen/risico's hierdoor): {klant_bijzonderheden}"
        ),
        backstory=(
            "Je bent een strategisch fiscaal adviseur die verder kijkt dan "
            "compliance. Je zoekt proactief naar fiscale voordelen en "
            "optimalisaties voor je klanten, altijd onderbouwd met wet- "
            "en vakliteratuur."
        ),
        llm_provider="gemini",
        llm_model="gemini-3-flash-preview",
        tools=["vpb_lookup", "vpb_boek_lookup"],
        max_iter=40,
        verbose=True,
    )

    # --- Agent 4: Fiscaal Review Manager ---
    manager_agent = TeamAgent.objects.create(
        team=team,
        order=4,
        role="Fiscaal Review Manager",
        goal=(
            "Leid de VPB-review door de specialisten per sectie van de aangifte "
            "aan te sturen. Combineer de wettelijke toetsing, praktische uitleg "
            "en fiscale adviezen tot een gestructureerd PDF-rapport.\n\n"
            "Bijzonderheden klant (markeer in rapport): {klant_bijzonderheden}"
        ),
        backstory=(
            "Je bent een senior fiscaal partner die teams aanstuurt bij "
            "complexe VPB-reviews. Je combineert juridische precisie met "
            "strategisch advies en levert professionele rapportages af."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-pro-preview",
        tools=["markdown_to_pdf"],
        max_iter=50,
        verbose=True,
        is_manager=True,
    )

    # --- Taak 1: OCR Extractie ---
    ocr_task = TeamTask.objects.create(
        team=team,
        order=0,
        description=(
            "Lees de volgende documenten in met de Mistral OCR tool:\n\n"
            "1. VPB-aangifte (verplicht): '{document_path}'\n"
            "2. Jaarrekening (indien pad niet leeg): '{jaarrekening_path}'\n"
            "3. Extra document (indien pad niet leeg): '{extra_document_path}'\n\n"
            "Lever per document de volledige tekst op als gestructureerde markdown. "
            "Markeer duidelijk welke tekst uit welk document komt.\n\n"
            "Identificeer in de VPB-aangifte de secties:\n" + VPB_SECTIES
        ),
        expected_output=(
            "De volledige tekst van de VPB-aangifte in gestructureerde markdown, "
            "met duidelijk gemarkeerde secties en alle cijfers nauwkeurig overgenomen."
        ),
        agent=ocr_agent,
    )

    # --- Taak 2: Wettelijke Toetsing per sectie ---
    wet_task = TeamTask.objects.create(
        team=team,
        order=1,
        description=(
            "Toets de VPB-aangifte per sectie aan de Wet Vpb 1969.\n\n"
            "Bijzonderheden klant: {klant_bijzonderheden}\n\n"
            "Doorloop per sectie met de vpb_wet_lookup tool:\n\n"
            "1. **Belastingplichtige** -> zoek: subjectieve belastingplicht, art. 1 Vpb, art. 2 Vpb, art. 3 Vpb\n"
            "2. **Investeringen** -> zoek: investeringsaftrek (regeling via art. 8 Vpb jo. Wet IB 2001)\n"
            "3. **Deelnemingen en vrijstelling** -> zoek: deelnemingsvrijstelling, art. 13 Vpb, art. 13a-13d Vpb\n"
            "4. **Balans: Activa** -> zoek: waardering activa, goed koopmansgebruik, financiele vaste activa\n"
            "5. **Balans: Passiva** -> zoek: ondernemingsvermogen, voorzieningen, schulden\n"
            "6. **Winst-en-verliesrekening** -> zoek: winst art. 7 Vpb, winstbepaling art. 8 Vpb, niet-aftrekbare kosten art. 10 Vpb\n"
            "7. **Aandeelhouders** -> zoek: informeel kapitaal art. 8bb-8bd Vpb, renteaftrek gelieerde partij art. 10a Vpb\n"
            "8. **Deelnemingen (detail)** -> zoek: art. 13 Vpb, liquidatieverlies art. 13d Vpb, fiscale eenheid art. 15 Vpb\n"
            "9. **Fiscale winst** -> zoek: belastbaar bedrag art. 7 Vpb, vermogensvergelijking\n"
            "10. **Houdsteractiviteiten** -> zoek: houdstermaatschappij, verliesverrekening art. 20 Vpb\n"
            "11. **Renteaftrekbeperking** -> zoek: earningsstripping art. 15b Vpb, anti-misbruik rente art. 10a Vpb\n"
            "12. **Overzicht belastbare winst** -> zoek: deelnemingsvrijstelling, belastbaar bedrag\n"
            "13. **Verliesverrekening** -> zoek: verliesverrekening art. 20 Vpb, carry-back, carry-forward\n"
            "14. **Overzicht belastingbedrag** -> zoek: VPB-tarief art. 22 Vpb, schijven\n\n"
            "Per sectie rapporteer:\n"
            "- Relevante wetsartikelen met nummer en lid\n"
            "- Of de aangifte conform de wet is\n"
            "- Specifieke afwijkingen of aandachtspunten"
        ),
        expected_output=(
            "Een gestructureerd rapport per sectie (1 t/m 14) met wetsartikelverwijzingen, "
            "conformiteitscheck en geconstateerde afwijkingen."
        ),
        agent=wet_agent,
    )
    wet_task.context_tasks.add(ocr_task)

    # --- Taak 3: Praktische Review per sectie ---
    boek_task = TeamTask.objects.create(
        team=team,
        order=2,
        description=(
            "Zoek per sectie van de VPB-aangifte de praktische uitleg op in "
            "'Wegwijs in de Vennootschapsbelasting'.\n\n"
            "Per sectie (1 t/m 14):\n"
            "- Zoek relevante passages en voorbeelden\n"
            "- Identificeer aandachtspunten en valkuilen\n"
            "- Noteer praktische interpretaties die afwijken van de letterlijke wet\n\n"
            "Secties om te doorlopen:\n" + VPB_SECTIES
        ),
        expected_output=(
            "Per sectie: praktische uitleg, relevante voorbeelden uit het vakboek, "
            "en aandachtspunten/valkuilen."
        ),
        agent=boek_agent,
    )
    boek_task.context_tasks.add(ocr_task)

    # --- Taak 4: Fiscaal Advies per sectie ---
    advies_task = TeamTask.objects.create(
        team=team,
        order=3,
        description=(
            "Analyseer de VPB-aangifte op fiscale optimalisatiemogelijkheden.\n\n"
            "Doorloop elke sectie en identificeer per sectie:\n"
            "- **Investeringen**: gemiste investeringsaftrek (KIA/EIA/MIA/VAMIL)\n"
            "- **Deelnemingen**: correcte toepassing deelnemingsvrijstelling, liquidatieverlies\n"
            "- **Balans**: herinvesteringsreserve, afwaardering vorderingen\n"
            "- **W&V**: niet-aftrekbare kosten correct verwerkt, gemengde kosten\n"
            "- **Aandeelhouders**: zakelijkheid schulden/vorderingen, rente art. 10a\n"
            "- **Houdsteractiviteiten**: gevolgen houdsterstatus voor verliesverrekening\n"
            "- **Renteaftrekbeperking**: optimalisatie binnen earningsstripping\n"
            "- **Verliesverrekening**: carry-back benut? carry-forward termijnen?\n"
            "- **Belastingbedrag**: correct tarief, mkb-schijf optimaal benut?\n\n"
            "Per kans rapporteer: potentieel voordeel, wetsartikel, benodigde actie."
        ),
        expected_output=(
            "Een overzicht van fiscale optimalisatiemogelijkheden per sectie, "
            "elk met wetsartikelverwijzing, potentieel voordeel en concrete actie."
        ),
        agent=advies_agent,
    )
    advies_task.context_tasks.add(ocr_task)
    advies_task.context_tasks.add(wet_task)
    advies_task.context_tasks.add(boek_task)

    # --- Taak 5: Rapport Samenstelling ---
    rapport_task = TeamTask.objects.create(
        team=team,
        order=4,
        description=(
            "Combineer alle bevindingen tot een professioneel PDF-rapport.\n\n"
            "Rapportstructuur:\n"
            "# VPB Fiscale Review\n\n"
            "Per sectie (1 t/m 14):\n"
            "### [Sectienaam]\n"
            "**Bevinding:** ...\n"
            "**Wettelijke grondslag:** Art. X Wet Vpb 1969 — ...\n"
            "**Toelichting (Wegwijs):** ...\n"
            "**Risico:** Laag / Midden / Hoog\n"
            "**Fiscale kansen:** ...\n\n"
            "### Samenvatting Bevindingen\n"
            "- Kernpunten\n\n"
            "### Fiscaal Advies — Optimalisatiemogelijkheden\n"
            "| Kans | Potentieel voordeel | Wetsartikel | Actie |\n\n"
            "Genereer het rapport als PDF via de markdown_to_pdf tool."
        ),
        expected_output=(
            "Een professioneel PDF-rapport met bevindingen per sectie, "
            "wetsverwijzingen, praktische toelichting en een overzichtstabel "
            "met fiscale optimalisatiemogelijkheden."
        ),
        agent=manager_agent,
    )
    rapport_task.context_tasks.add(wet_task)
    rapport_task.context_tasks.add(boek_task)
    rapport_task.context_tasks.add(advies_task)


def reverse_seed(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    team = Team.objects.filter(slug="vpb-fiscale-review").first()
    if team:
        team.agents.all().delete()
        team.variables.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0078_add_fiscale_wet_and_vpb_boek_models"),
    ]

    operations = [
        migrations.RunPython(seed_vpb_review_team, reverse_seed),
    ]
