"""
Data migration: seed the two built-in teams (Dependency Monitor, Bedrijfsmonitor)
into the Team Builder tables so they are immediately editable via the UI.
"""

from django.db import migrations


def seed_teams(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    TeamVariable = apps.get_model("dashboard", "TeamVariable")
    TeamAgent = apps.get_model("dashboard", "TeamAgent")
    TeamTask = apps.get_model("dashboard", "TeamTask")

    # ---------------------------------------------------------------
    # Team 1: Dependency Monitor
    # ---------------------------------------------------------------
    dep_team = Team.objects.create(
        name="Dependency Monitor",
        slug="dependency-monitor",
        description="Scant Python dependencies op verouderde packages, beveiligingslekken, API-deprecaties en breaking changes.",
        process="sequential",
        verbose=True,
    )

    TeamVariable.objects.create(
        team=dep_team,
        name="requirements_path",
        label="Pad naar requirements.txt",
        description="Volledig pad naar het requirements.txt bestand van het te scannen project.",
        input_type="file_path",
        default_value="",
        required=True,
        order=0,
    )

    # Agents
    dep_scanner = TeamAgent.objects.create(
        team=dep_team, order=0,
        role="Dependency Scanner",
        goal=(
            "Scan the requirements.txt of the monitored Django project and identify all "
            "packages that have newer versions available on PyPI. Focus on MAJOR version "
            "updates and security patches. Ignore minor/patch updates unless they are "
            "security-related."
        ),
        backstory=(
            "You are a meticulous Python package analyst. You know the Python ecosystem "
            "inside out and can quickly identify which package updates are critical and "
            "which are safe to ignore. You always check PyPI for the latest stable versions."
        ),
        llm_provider="gemini", llm_model="gemini-3-flash-preview",
        tools=["requirements_reader", "pypi_checker"],
        max_iter=80, verbose=True,
    )

    api_monitor = TeamAgent.objects.create(
        team=dep_team, order=1,
        role="API Deprecation Monitor",
        goal=(
            "Check the status of all monitored APIs (Meta/WhatsApp Graph API, Stripe, "
            "Django) and determine if any are deprecated, approaching sunset, or have "
            "already been sunset. Flag any API version that requires immediate action."
        ),
        backstory=(
            "You are an API lifecycle expert who has seen too many production outages "
            "caused by deprecated APIs. You know exactly how Meta, Stripe, and Django "
            "handle API versioning and deprecation. You never miss a sunset date."
        ),
        llm_provider="gemini", llm_model="gemini-3-flash-preview",
        tools=["api_status_checker"],
        max_iter=40, verbose=True,
    )

    security_checker = TeamAgent.objects.create(
        team=dep_team, order=2,
        role="Security Vulnerability Checker",
        goal=(
            "Check all project dependencies against the OSV.dev vulnerability database. "
            "Focus on CRITICAL and HIGH severity vulnerabilities that need immediate "
            "patching. Provide the CVE/GHSA identifier and the fixed version."
        ),
        backstory=(
            "You are a cybersecurity analyst specializing in supply chain security. "
            "You monitor vulnerability databases daily and know which CVEs are actively "
            "exploited. You prioritize findings by real-world impact, not just CVSS scores."
        ),
        llm_provider="gemini", llm_model="gemini-3-flash-preview",
        tools=["vuln_scanner"],
        max_iter=50, verbose=True,
    )

    breaking_analyzer = TeamAgent.objects.create(
        team=dep_team, order=3,
        role="Breaking Change Analyzer",
        goal=(
            "For packages that are significantly outdated, fetch their GitHub release notes "
            "and identify ONLY breaking changes and deprecations. Explain what will break "
            "if the project doesn't upgrade, and what needs to change in code."
        ),
        backstory=(
            "You are a senior Django developer who has performed dozens of major dependency "
            "upgrades. You know exactly which changes in release notes actually affect "
            "running applications and which are irrelevant. You focus on actionable insights."
        ),
        llm_provider="gemini", llm_model="gemini-3-flash-preview",
        tools=["github_changelog"],
        max_iter=40, verbose=True,
    )

    report_writer = TeamAgent.objects.create(
        team=dep_team, order=4,
        role="Action Report Writer",
        goal=(
            "Compile all findings from the other agents into a clear, actionable report. "
            "Determine the overall status (CRITICAL/WARNING/OK). Generate concrete "
            "implementation steps for each finding. Include a relevant dev tip for the "
            "Django/Celery/Python stack and a motivational quote about resilience. "
            "Send the report via email. ALWAYS send an email, even if everything is OK."
        ),
        backstory=(
            "You are a technical writer who creates reports that developers actually read "
            "and act on. You write in Dutch (Netherlands) and keep things concise but "
            "complete. Your reports have saved countless production systems from outages. "
            "You believe every weekly check deserves a report - even good news."
        ),
        llm_provider="gemini", llm_model="gemini-3.1-pro-preview",
        tools=["email_sender"],
        max_iter=25, verbose=True,
    )

    # Tasks
    scan_task = TeamTask.objects.create(
        team=dep_team, order=0,
        description=(
            "Read the requirements.txt file at {requirements_path} and check each package "
            "against PyPI for the latest stable version.\n\n"
            "For each package:\n"
            "1. Get the current pinned/constrained version from requirements.txt\n"
            "2. Check PyPI for the latest stable version\n"
            "3. Determine if the update is: MAJOR (breaking), SECURITY patch, or minor\n\n"
            "Only report packages that are:\n"
            "- A MAJOR version behind (e.g., Django 4.x when 5.x is available)\n"
            "- Have a known security patch available\n"
            "- Are significantly outdated (>2 minor versions behind)"
        ),
        expected_output=(
            "A structured list of packages needing attention, with their current version, "
            "latest version, update type, and GitHub URL. Also include the total count "
            "of packages scanned."
        ),
        agent=dep_scanner,
    )

    api_task = TeamTask.objects.create(
        team=dep_team, order=1,
        description=(
            "Check the deprecation status of all monitored APIs configured in the "
            "monitored_apis.yaml file.\n\n"
            "For each API:\n"
            "1. Fetch the API status/changelog page\n"
            "2. Analyze whether our current version is deprecated or approaching sunset\n"
            "3. Determine the recommended version to upgrade to\n"
            "4. Identify the sunset/end-of-life date if available"
        ),
        expected_output=(
            "For each monitored API: the current status (active/deprecated/sunset), "
            "the recommended version, any sunset dates, and whether action is needed."
        ),
        agent=api_monitor,
    )

    vuln_task = TeamTask.objects.create(
        team=dep_team, order=2,
        description=(
            "For each package identified in the dependency scan, check the OSV.dev "
            "vulnerability database for known security issues.\n\n"
            "Focus on:\n"
            "1. CRITICAL severity (CVSS >= 9.0) - immediate action required\n"
            "2. HIGH severity (CVSS >= 7.0) - action required soon\n"
            "3. Skip MEDIUM and LOW unless they are actively exploited"
        ),
        expected_output=(
            "A list of vulnerabilities found, grouped by severity (CRITICAL first), "
            "with CVE identifiers, descriptions, and fixed versions. If no vulnerabilities "
            "are found, explicitly state that."
        ),
        agent=security_checker,
    )
    vuln_task.context_tasks.add(scan_task)

    breaking_task = TeamTask.objects.create(
        team=dep_team, order=3,
        description=(
            "For each significantly outdated package (MAJOR version behind or with breaking "
            "changes noted), fetch the GitHub release notes and analyze them.\n\n"
            "Focus ONLY on:\n"
            "1. Breaking changes that would cause errors in existing code\n"
            "2. Deprecated features that will be removed\n"
            "3. Required migration steps"
        ),
        expected_output=(
            "For each analyzed package: a summary of breaking changes, what will break "
            "in the codebase, and required code changes. If no breaking changes, state "
            "that the upgrade is safe."
        ),
        agent=breaking_analyzer,
    )
    breaking_task.context_tasks.add(scan_task)

    report_task = TeamTask.objects.create(
        team=dep_team, order=4,
        description=(
            "Compile all findings from previous agents into a comprehensive report and "
            "send it via email. The report MUST be in Dutch (Netherlands).\n\n"
            "ALWAYS send an email, regardless of whether action is needed or not.\n\n"
            "1. Determine overall status:\n"
            "   - CRITICAL: Security vulnerabilities, API sunset, app broken\n"
            "   - WARNING: API deprecation soon, major version behind\n"
            "   - OK: Everything up-to-date, no issues\n\n"
            "2. For each finding, provide CONCRETE implementation steps."
        ),
        expected_output=(
            "Confirmation that the email was sent, along with the full report content "
            "including status, findings, action steps, tip, and quote."
        ),
        agent=report_writer,
    )
    report_task.context_tasks.add(scan_task, api_task, vuln_task, breaking_task)

    # ---------------------------------------------------------------
    # Team 2: Bedrijfsmonitor
    # ---------------------------------------------------------------
    fiscal_team = Team.objects.create(
        name="Bedrijfsmonitor",
        slug="bedrijfsmonitor",
        description="Onderzoekt Nederlandse fiscale ontwikkelingen en schrijft blog-artikelen voor MKB-ondernemers.",
        process="sequential",
        verbose=True,
    )

    # Agents
    fiscal_researcher = TeamAgent.objects.create(
        team=fiscal_team, order=0,
        role="Fiscaal Onderzoeker",
        goal=(
            "Doorzoek Nederlandse overheidsbronnen (belastingdienst.nl, rijksoverheid.nl, kvk.nl) "
            "op recente fiscale ontwikkelingen, wetswijzigingen en nieuws dat relevant is voor "
            "het MKB. Focus op BTW, inkomstenbelasting, vennootschapsbelasting, loonbelasting, "
            "subsidies en aankomende deadlines."
        ),
        backstory=(
            "Je bent een ervaren fiscaal onderzoeker die dagelijks de Nederlandse overheidswebsites "
            "monitort op veranderingen in belastingwetgeving. Je kent alle relevante bronnen en "
            "weet precies waar je moet zoeken voor de meest actuele informatie."
        ),
        llm_provider="gemini", llm_model="gemini-3-flash-preview",
        tools=["gov_site_fetcher", "tax_news_searcher", "deadline_checker"],
        max_iter=50, verbose=True,
    )

    trend_analyst = TeamAgent.objects.create(
        team=fiscal_team, order=1,
        role="Trend Analist",
        goal=(
            "Analyseer de gevonden fiscale ontwikkelingen op urgentie en impact voor het MKB. "
            "Selecteer de 2-4 meest relevante onderwerpen en maak een schrijfbriefing per "
            "onderwerp met context, kernpunten en doelgroep."
        ),
        backstory=(
            "Je bent een strategisch analist met expertise in Nederlandse belastingwetgeving "
            "en MKB-beleid. Je kunt snel inschatten welke ontwikkelingen de grootste impact "
            "hebben op ondernemers en welke onderwerpen prioriteit verdienen."
        ),
        llm_provider="gemini", llm_model="gemini-3-flash-preview",
        tools=[], max_iter=25, verbose=True,
    )

    blog_writer = TeamAgent.objects.create(
        team=fiscal_team, order=2,
        role="Blog Schrijver",
        goal=(
            "Schrijf professionele, goed leesbare blog-artikelen over fiscale onderwerpen "
            "voor MKB-ondernemers. Elk artikel heeft een pakkende titel, een korte intro "
            "(2-3 zinnen), en een uitgebreide body in markdown. Schrijf in het Nederlands, "
            "begrijpelijk maar inhoudelijk correct. Vermeld altijd de bronnen."
        ),
        backstory=(
            "Je bent een ervaren financieel journalist die complexe fiscale onderwerpen "
            "vertaalt naar begrijpelijke artikelen voor ondernemers. Je schrijft helder, "
            "concreet en actiegericht. Je vermijdt jargon maar bent inhoudelijk correct."
        ),
        llm_provider="gemini", llm_model="gemini-3-flash-preview",
        tools=[], max_iter=25, verbose=True,
    )

    quality_reviewer = TeamAgent.objects.create(
        team=fiscal_team, order=3,
        role="Kwaliteitsreviewer",
        goal=(
            "Review elk artikel op feitelijke correctheid, bronvermelding, leesbaarheid "
            "en relevantie. Geef een kwaliteitsscore van 1-10. Controleer of bronnen "
            "kloppen en of de informatie actueel is. Lever het eindresultaat als JSON array."
        ),
        backstory=(
            "Je bent een senior redacteur met een achtergrond in fiscaal recht. Je controleert "
            "artikelen op fouten, onvolledigheden en misleidende informatie. Je bent streng "
            "maar eerlijk in je beoordeling en zorgt ervoor dat alleen kwalitatieve content "
            "wordt gepubliceerd."
        ),
        llm_provider="gemini", llm_model="gemini-3.1-pro-preview",
        tools=["gov_site_fetcher"],
        max_iter=30, verbose=True,
    )

    # Tasks
    research_task = TeamTask.objects.create(
        team=fiscal_team, order=0,
        description=(
            "Doorzoek de volgende Nederlandse overheidsbronnen op recente fiscale ontwikkelingen "
            "die relevant zijn voor het MKB:\n"
            "- belastingdienst.nl (BTW, IB, VPB, loonbelasting)\n"
            "- rijksoverheid.nl (belastingplan, wetswijzigingen)\n"
            "- kvk.nl / ondernemersplein.kvk.nl (MKB subsidies, regelingen)\n\n"
            "Gebruik de Tax News Searcher, Fiscal Deadline Checker en Government Site Fetcher tools."
        ),
        expected_output=(
            "Een gestructureerd overzicht van 5-10 gevonden fiscale ontwikkelingen, elk met: "
            "titel/onderwerp, samenvatting, categorie, bron-URL en relevantie voor MKB."
        ),
        agent=fiscal_researcher,
    )

    analyze_task = TeamTask.objects.create(
        team=fiscal_team, order=1,
        description=(
            "Analyseer de gevonden fiscale ontwikkelingen en bepaal welke onderwerpen het meest "
            "relevant en urgent zijn voor MKB-ondernemers. Selecteer 2-4 onderwerpen voor "
            "blog-artikelen op basis van urgentie, impact, actualiteit en actiegerichtheid."
        ),
        expected_output=(
            "2-4 gedetailleerde schrijfbriefings, elk met voorgestelde titel, kernpunten, "
            "doelgroep, categorie en bronnen."
        ),
        agent=trend_analyst,
    )
    analyze_task.context_tasks.add(research_task)

    write_task = TeamTask.objects.create(
        team=fiscal_team, order=2,
        description=(
            "Schrijf op basis van de schrijfbriefings 2-4 professionele blog-artikelen in het "
            "Nederlands voor MKB-ondernemers. Elk artikel bevat title, intro, body (markdown), "
            "category en sources."
        ),
        expected_output=(
            "2-4 complete artikelen, elk met title, intro, body (markdown), category en sources."
        ),
        agent=blog_writer,
    )
    write_task.context_tasks.add(research_task, analyze_task)

    review_task = TeamTask.objects.create(
        team=fiscal_team, order=3,
        description=(
            "Review elk geschreven artikel op feitelijke correctheid, bronvermelding, leesbaarheid "
            "en compleetheid. Geef een quality_score van 1-10.\n\n"
            "Lever het eindresultaat als een geldige JSON array met het format:\n"
            '[{"title": "...", "intro": "...", "body": "...", "category": "...", '
            '"sources": ["..."], "quality_score": 8}]'
        ),
        expected_output=(
            "Een geldige JSON array met 2-4 artikel-objecten, elk met title, intro, body, "
            "category, sources en quality_score."
        ),
        agent=quality_reviewer,
    )
    review_task.context_tasks.add(write_task)


def unseed_teams(apps, schema_editor):
    Team = apps.get_model("dashboard", "Team")
    Team.objects.filter(slug__in=["dependency-monitor", "bedrijfsmonitor"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0006_add_team_builder"),
    ]

    operations = [
        migrations.RunPython(seed_teams, unseed_teams),
    ]
