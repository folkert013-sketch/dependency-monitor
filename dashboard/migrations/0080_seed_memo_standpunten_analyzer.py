"""Seed het Memo & Standpunten Analyzer team met hiërarchisch process."""

from django.db import migrations


def seed_memo_standpunten_team(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamVariable = apps.get_model("dashboard", "TeamVariable")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")
    User = apps.get_model("auth", "User")

    owner = User.objects.filter(is_superuser=True).first()

    team = Team.objects.filter(slug="memo-standpunten-analyzer").first()
    if not team:
        team = Team.objects.create(
            name="Memo & Standpunten Analyzer",
            slug="memo-standpunten-analyzer",
            description=(
                "Analyseert fiscale memo's en standpunten vanuit meerdere "
                "invalshoeken: verdediging, aanval/verdediging en fiscaal advies. "
                "Levert een PDF-rapport, herschreven memo of brief aan de "
                "Belastingdienst. Domein-wisselbaar via de {domein} variabele "
                "(vpb/ib)."
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
        name="domein",
        label="Fiscaal domein",
        description="Keuze: vpb of ib. Bepaalt welke wetgevings- en tarieventools worden gebruikt.",
        input_type="text",
        default_value="vpb",
        required=True,
        order=0,
    )
    TeamVariable.objects.create(
        team=team,
        name="document_path",
        label="Memo / Standpunt PDF",
        description="Upload het memo, standpunt of adviesdocument als PDF.",
        input_type="file_path",
        default_value="",
        required=True,
        order=1,
    )
    TeamVariable.objects.create(
        team=team,
        name="boekjaar",
        label="Boekjaar",
        description="Het fiscale boekjaar waarop het document betrekking heeft. Tarieven en regelgeving worden voor dit jaar opgezocht.",
        input_type="text",
        default_value="2023",
        required=True,
        order=2,
    )
    TeamVariable.objects.create(
        team=team,
        name="analyse_richting",
        label="Analyse richting",
        description="Keuze: 'verdediging', 'aanval_en_verdediging', 'fiscaal_advies', of 'alle' (alle drie).",
        input_type="text",
        default_value="alle",
        required=False,
        order=3,
    )
    TeamVariable.objects.create(
        team=team,
        name="output_formaat",
        label="Gewenst output formaat",
        description="Keuze: 'herschreven_memo', 'brief_belastingdienst', 'review' (gestructureerde review per onderwerp), of 'alle'.",
        input_type="text",
        default_value="review",
        required=True,
        order=4,
    )
    TeamVariable.objects.create(
        team=team,
        name="klant_context",
        label="Klant context en bijzonderheden",
        description="Relevante achtergrond: type onderneming, branche, eerdere correspondentie met Belastingdienst, specifieke geschilpunten.",
        input_type="textarea",
        default_value="",
        required=False,
        order=5,
    )
    TeamVariable.objects.create(
        team=team,
        name="extra_document_path",
        label="Extra document PDF",
        description="Optioneel: eerdere brief van de Belastingdienst, jaarrekening of eerder standpunt.",
        input_type="file_path",
        default_value="",
        required=False,
        order=6,
    )

    # --- Agent 0: OCR Specialist ---
    ocr_agent = TeamAgent.objects.create(
        team=team,
        order=0,
        role="Document OCR Specialist",
        goal=(
            "Lees de volgende documenten in via OCR en lever de volledige tekst "
            "op als gestructureerde markdown:\n\n"
            "1. Memo/standpunt (verplicht): '{document_path}'\n"
            "2. Extra document (indien aanwezig): '{extra_document_path}'\n\n"
            "Behoud de oorspronkelijke structuur: paragrafen, kopjes, opsommingen, "
            "bedragen en verwijzingen. Markeer duidelijk per document welke "
            "informatie eruit komt."
        ),
        backstory=(
            "Je bent een documentspecialist getraind in het verwerken van "
            "fiscale memo's, standpunten en adviesdocumenten. Je herkent "
            "juridische structuur, artikelverwijzingen en bedragen feilloos."
        ),
        llm_provider="gemini",
        llm_model="gemini-3-flash-preview",
        tools=["mistral_ocr"],
        max_iter=10,
        verbose=True,
    )

    # --- Agent 1: Memo Structuuranalist ---
    structuur_agent = TeamAgent.objects.create(
        team=team,
        order=1,
        role="Memo Structuuranalist",
        goal=(
            "Analyseer het memo/standpunt en splits het op in afzonderlijke "
            "onderwerpen (topics). Per onderwerp identificeer je:\n"
            "1. Het fiscale onderwerp (bijv. 'verliesverrekening', "
            "'deelnemingsvrijstelling', 'box 2 inkomen')\n"
            "2. Het ingenomen standpunt of de positie\n"
            "3. De kern van de argumentatie\n"
            "4. Genoemde bedragen, percentages of jaartallen\n"
            "5. Eventuele artikelverwijzingen in het origineel\n\n"
            "Boekjaar: {boekjaar}\n"
            "Klant context: {klant_context}"
        ),
        backstory=(
            "Je bent een ervaren fiscaal jurist die complexe memo's snel kan "
            "ontleden in de kernonderwerpen. Je herkent waar een nieuw argument "
            "of standpunt begint en kunt de essentie in enkele zinnen samenvatten."
        ),
        llm_provider="gemini",
        llm_model="gemini-3-flash-preview",
        tools=[],
        max_iter=15,
        verbose=True,
    )

    # --- Agent 2: Fiscaal Wetgevingsspecialist ---
    wet_agent = TeamAgent.objects.create(
        team=team,
        order=2,
        role="Fiscaal Wetgevingsspecialist",
        goal=(
            "Toets per onderwerp uit het memo de relevante fiscale wetgeving "
            "voor boekjaar {boekjaar}.\n\n"
            "BELANGRIJK:\n"
            "- Gebruik ALTIJD de {domein}_lookup tool voor wetsartikelen\n"
            "- Gebruik de {domein}_boek_lookup tool voor praktische uitleg "
            "(indien beschikbaar)\n"
            "- Gebruik de {domein}_tarieven tool voor tarieven en "
            "drempelbedragen — geef altijd het boekjaar mee (bijv. "
            "'tarief | {boekjaar}')\n"
            "- Gebruik NOOIT je trainingsdata voor tarieven, percentages of "
            "drempelbedragen\n\n"
            "Per onderwerp:\n"
            "1. Zoek de relevante wetsartikelen op\n"
            "2. Zoek de praktische uitleg op (indien boek-tool beschikbaar)\n"
            "3. Noteer geldende tarieven en drempels voor boekjaar {boekjaar}\n"
            "4. Beoordeel of het ingenomen standpunt wettelijk onderbouwd is\n\n"
            "Klant context: {klant_context}"
        ),
        backstory=(
            "Je bent een fiscaal jurist gespecialiseerd in de Nederlandse "
            "belastingwetgeving. Je kent de relevante wetteksten door en door "
            "en gebruikt altijd de officiële wetteksten — nooit je geheugen — "
            "voor tarieven en regelgeving. Je bent nauwgezet in "
            "artikelverwijzingen."
        ),
        llm_provider="gemini",
        llm_model="gemini-3-flash-preview",
        tools=["{domein}_lookup", "{domein}_boek_lookup", "{domein}_tarieven"],
        max_iter=40,
        verbose=True,
    )

    # --- Agent 3: Standpunten Analist ---
    standpunten_agent = TeamAgent.objects.create(
        team=team,
        order=3,
        role="Standpunten Analist",
        goal=(
            "Analyseer elk onderwerp uit het memo vanuit de gevraagde "
            "invalshoek(en): {analyse_richting}\n\n"
            "De drie mogelijke invalshoeken:\n"
            "1. VERDEDIGING — Versterk het ingenomen standpunt. Zoek "
            "ondersteunende wetsartikelen en praktische uitleg die het "
            "standpunt onderbouwen.\n"
            "2. AANVAL EN VERDEDIGING — Identificeer zwakke plekken in het "
            "standpunt die de Belastingdienst zou kunnen aanvallen. Formuleer "
            "vervolgens tegenargumenten voor elke zwakte.\n"
            "3. FISCAAL ADVIES — Identificeer fiscale kansen en risico's die "
            "nog niet in het memo staan. Denk aan gemiste aftrekposten, "
            "optimalisaties of onbenutte faciliteiten voor boekjaar "
            "{boekjaar}.\n\n"
            "Als analyse_richting = 'alle': lever alle drie de invalshoeken "
            "per onderwerp.\n"
            "Als analyse_richting een specifieke keuze is: lever alleen die "
            "invalshoek.\n\n"
            "BELANGRIJK: Onderbouw ELK argument met exacte "
            "wetsartikelverwijzingen. Gebruik de {domein}_lookup en "
            "{domein}_boek_lookup tools. Gebruik {domein}_tarieven voor "
            "tarieven (geef boekjaar mee). Baseer GEEN tarieven of regels op "
            "trainingsdata.\n\n"
            "Klant context: {klant_context}"
        ),
        backstory=(
            "Je bent een strategisch fiscaal adviseur en procesgemachtigde "
            "met ervaring in bezwaar- en beroepsprocedures tegen de "
            "Belastingdienst. Je kunt elk standpunt van meerdere kanten "
            "belichten: versterken, aanvallen en adviseren. Je onderbouwt "
            "altijd met wetsartikelen en praktische voorbeelden."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-pro-preview",
        tools=["{domein}_lookup", "{domein}_boek_lookup", "{domein}_tarieven"],
        max_iter=40,
        verbose=True,
    )

    # --- Agent 4: Rapport Schrijver ---
    rapport_agent = TeamAgent.objects.create(
        team=team,
        order=4,
        role="Rapport Schrijver",
        goal=(
            "Stel het eindproduct samen op basis van het gevraagde formaat: "
            "{output_formaat}\n\n"
            "Mogelijke formaten:\n"
            "1. 'herschreven_memo' — Herschrijf het originele memo/standpunt "
            "met verwerking van alle analyses. Versterk de argumentatie, voeg "
            "wetsverwijzingen toe, en verwerk de gekozen analyse-richting.\n"
            "2. 'brief_belastingdienst' — Schrijf een formele brief aan de "
            "Belastingdienst ter verdediging van het standpunt. Gebruik "
            "zakelijke toon, structureer per onderwerp, en onderbouw met "
            "exacte wetsartikelen.\n"
            "3. 'review' — Maak een gestructureerde review per onderwerp met: "
            "origineel standpunt, wetgevingstoets, verdediging, "
            "aanval/verdediging en fiscaal advies in overzichtelijke secties.\n"
            "4. 'alle' — Genereer alle drie de bovenstaande formaten.\n\n"
            "Boekjaar: {boekjaar}\n"
            "Genereer het rapport als PDF via de markdown_to_pdf tool."
        ),
        backstory=(
            "Je bent een senior fiscaal partner die professionele rapporten, "
            "memo's en brieven aan de Belastingdienst schrijft. Je combineert "
            "juridische precisie met heldere communicatie en levert "
            "publicatie-klare documenten af."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-pro-preview",
        tools=["markdown_to_pdf"],
        max_iter=30,
        verbose=True,
    )

    # --- Agent 5: Fiscaal Review Manager ---
    manager_agent = TeamAgent.objects.create(
        team=team,
        order=5,
        role="Fiscaal Review Manager",
        goal=(
            "Stuur de memo-analyse aan door de specialisten per fase te "
            "coördineren. Evalueer na elke stap of de tussenresultaten "
            "compleet en kwalitatief voldoende zijn. Bepaal of extra "
            "verdieping nodig is op specifieke onderwerpen.\n\n"
            "Zorg dat:\n"
            "- Elk onderwerp uit het memo volledig is geanalyseerd\n"
            "- Wetsverwijzingen correct en specifiek zijn voor boekjaar "
            "{boekjaar}\n"
            "- De gevraagde analyse-invalshoek(en) ({analyse_richting}) "
            "compleet zijn uitgewerkt\n"
            "- Het eindresultaat aansluit bij het gevraagde formaat "
            "({output_formaat})\n"
            "- Bijzonderheden uit de klant context zijn meegenomen: "
            "{klant_context}"
        ),
        backstory=(
            "Je bent een senior fiscaal partner die teams aanstuurt bij "
            "complexe memo-analyses. Je evalueert de kwaliteit van "
            "tussenresultaten, identificeert leemtes, en zorgt dat het "
            "eindproduct volledig en professioneel is."
        ),
        llm_provider="gemini",
        llm_model="gemini-3.1-pro-preview",
        tools=[],
        max_iter=50,
        verbose=True,
        is_manager=True,
    )

    # --- Taak 0: OCR Extractie ---
    ocr_task = TeamTask.objects.create(
        team=team,
        order=0,
        description=(
            "Lees de volgende documenten in met de Mistral OCR tool:\n\n"
            "1. Memo/standpunt (verplicht): '{document_path}'\n"
            "2. Extra document (indien pad niet leeg): '{extra_document_path}'\n\n"
            "Lever per document de volledige tekst op als gestructureerde "
            "markdown. Markeer duidelijk welke tekst uit welk document komt. "
            "Behoud alle paragrafen, kopjes, bedragen en verwijzingen."
        ),
        expected_output=(
            "De volledige tekst van het memo/standpunt in gestructureerde "
            "markdown, met alle paragrafen, kopjes, bedragen en verwijzingen "
            "nauwkeurig overgenomen. Indien een extra document is meegegeven, "
            "apart gemarkeerd."
        ),
        agent=ocr_agent,
    )

    # --- Taak 1: Onderwerp Extractie ---
    onderwerp_task = TeamTask.objects.create(
        team=team,
        order=1,
        description=(
            "Splits het memo/standpunt op in afzonderlijke onderwerpen.\n\n"
            "Per onderwerp lever:\n"
            "1. Het fiscale onderwerp\n"
            "2. Het ingenomen standpunt of de positie\n"
            "3. De kern van de argumentatie\n"
            "4. Genoemde bedragen, percentages of jaartallen\n"
            "5. Eventuele artikelverwijzingen\n\n"
            "Boekjaar: {boekjaar}\n"
            "Klant context: {klant_context}"
        ),
        expected_output=(
            "Een genummerde lijst van onderwerpen, per onderwerp: (1) het "
            "fiscale onderwerp, (2) het ingenomen standpunt, (3) "
            "kernargumentatie, (4) relevante bedragen/percentages, (5) "
            "originele artikelverwijzingen."
        ),
        agent=structuur_agent,
    )
    onderwerp_task.context_tasks.add(ocr_task)

    # --- Taak 2: Wetgevingstoetsing ---
    wet_task = TeamTask.objects.create(
        team=team,
        order=2,
        description=(
            "Toets per onderwerp de relevante fiscale wetgeving voor boekjaar "
            "{boekjaar}.\n\n"
            "Gebruik de {domein}_lookup tool voor wetsartikelen, de "
            "{domein}_boek_lookup tool voor praktische uitleg (indien "
            "beschikbaar), en de {domein}_tarieven tool voor tarieven (geef "
            "altijd het boekjaar mee, bijv. 'tarief | {boekjaar}').\n\n"
            "Per onderwerp:\n"
            "1. Zoek de relevante wetsartikelen op\n"
            "2. Noteer geldende tarieven en drempels voor {boekjaar}\n"
            "3. Beoordeel of het standpunt wettelijk onderbouwd is: "
            "onderbouwd / niet onderbouwd / deels onderbouwd\n\n"
            "Klant context: {klant_context}"
        ),
        expected_output=(
            "Per onderwerp: een overzicht van relevante wetsartikelen (met "
            "artikelnummer en lid), geldende tarieven voor boekjaar {boekjaar}, "
            "en een conformiteitsoordeel (onderbouwd/niet onderbouwd/deels "
            "onderbouwd)."
        ),
        agent=wet_agent,
    )
    wet_task.context_tasks.add(ocr_task)
    wet_task.context_tasks.add(onderwerp_task)

    # --- Taak 3: Driehoeksanalyse ---
    analyse_task = TeamTask.objects.create(
        team=team,
        order=3,
        description=(
            "Analyseer elk onderwerp vanuit de gevraagde invalshoek(en): "
            "{analyse_richting}\n\n"
            "1. VERDEDIGING — Versterk het standpunt met ondersteunende "
            "artikelen en argumenten.\n"
            "2. AANVAL EN VERDEDIGING — Identificeer zwakke plekken + "
            "formuleer tegenargumenten.\n"
            "3. FISCAAL ADVIES — Identificeer gemiste kansen en risico's voor "
            "boekjaar {boekjaar}.\n\n"
            "Gebruik de {domein}_lookup, {domein}_boek_lookup en "
            "{domein}_tarieven tools. Onderbouw ELK argument met exacte "
            "artikelverwijzingen.\n\n"
            "Als analyse_richting = 'alle': lever alle drie per onderwerp.\n"
            "Als specifieke keuze: lever alleen die invalshoek.\n\n"
            "Klant context: {klant_context}"
        ),
        expected_output=(
            "Per onderwerp de gevraagde analyse-invalshoek(en) "
            "({analyse_richting}), elk argument onderbouwd met exacte "
            "wetsartikelverwijzingen. Bij 'alle': drie duidelijk gescheiden "
            "secties per onderwerp."
        ),
        agent=standpunten_agent,
    )
    analyse_task.context_tasks.add(ocr_task)
    analyse_task.context_tasks.add(onderwerp_task)
    analyse_task.context_tasks.add(wet_task)

    # --- Taak 4: Output Generatie ---
    output_task = TeamTask.objects.create(
        team=team,
        order=4,
        description=(
            "Stel het eindproduct samen in het gevraagde formaat: "
            "{output_formaat}\n\n"
            "Mogelijke formaten:\n"
            "- 'herschreven_memo': herschrijf het memo met verwerkte analyses "
            "en wetsverwijzingen\n"
            "- 'brief_belastingdienst': formele brief ter verdediging, "
            "zakelijke toon, per onderwerp\n"
            "- 'review': gestructureerde review per onderwerp met alle "
            "invalshoeken\n"
            "- 'alle': genereer alle drie\n\n"
            "Boekjaar: {boekjaar}\n"
            "Genereer het rapport als PDF via de markdown_to_pdf tool."
        ),
        expected_output=(
            "Een professioneel PDF-document in het gevraagde formaat "
            "({output_formaat}), met correcte wetsverwijzingen, zakelijke "
            "toon en publicatie-klare opmaak."
        ),
        agent=rapport_agent,
    )
    output_task.context_tasks.add(onderwerp_task)
    output_task.context_tasks.add(wet_task)
    output_task.context_tasks.add(analyse_task)


def reverse_seed(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    team = Team.objects.filter(slug="memo-standpunten-analyzer").first()
    if team:
        team.agents.all().delete()
        team.variables.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0079_seed_vpb_review_team"),
    ]

    operations = [
        migrations.RunPython(seed_memo_standpunten_team, reverse_seed),
    ]
