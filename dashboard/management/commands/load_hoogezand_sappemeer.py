"""
Management command: laad 61 MKB-bedrijven uit Hoogezand-Sappemeer als prospects.

Drie categorieën: bouw (22), installatie (19), productie (20).

Usage:
    python manage.py load_hoogezand_sappemeer
"""

from django.core.management.base import BaseCommand

from dashboard.models import Prospect, ProspectGroup
from dashboard.services.prospect_dedup import find_existing_prospect

# ---------------------------------------------------------------------------
# Categorie 1: Bouwbedrijven en aannemers (22)
# ---------------------------------------------------------------------------
BOUWBEDRIJVEN = [
    {
        "name": "Aannemersbedrijf Lamein B.V.",
        "address": "De Vosholen 2C, 9611 KR Sappemeer",
        "website": "lamein.com",
        "email": "",
        "phone": "0598-323848",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1924\n"
            "Medewerkers: ~20\n"
            "Specialisatie: Timmerbedrijf & aannemer; industriële bouwwerken "
            "(chemie, voedingsmiddelen)"
        ),
    },
    {
        "name": "Bouw- en Interieurbouwbedrijf Wilbrink B.V.",
        "address": "Sappemeer (Kalkwijk)",
        "website": "wilbrinkhoogezand.nl",
        "email": "",
        "phone": "0598-327084",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: ca. 1872\n"
            "Specialisatie: Bedrijfspanden, winkels, kantoren, woningen, "
            "interieurbouw\n"
            "Opmerking: Familiebedrijf"
        ),
    },
    {
        "name": "Bouwbedrijf Germeraad",
        "address": "Noorderstraat 216, 9611 AR Sappemeer",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Specialisatie: Nieuwbouw, verbouwingen voor particulieren en bedrijven",
    },
    {
        "name": "Aannemingsbedrijf Venema B.V.",
        "address": "Verdilaan 7, 9603 AP Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Specialisatie: Burgerlijke en utiliteitsbouw",
    },
    {
        "name": "Peter Knol Bouwbedrijf B.V.",
        "address": "Onnen (actief Hoogezand e.o.)",
        "website": "peterknolbouwbedrijf.nl",
        "email": "",
        "phone": "050-4042428",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1998\n"
            "Specialisatie: Nieuwbouw, verbouw, renovatie, isolatie\n"
            "Opmerking: VCA-gecertificeerd"
        ),
    },
    {
        "name": "Aannemersbedrijf J. Kuit V.O.F.",
        "address": "Sluisweg 62-68, 9605 PT Kiel-Windeweer",
        "website": "aannemerkuit.nl",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Medewerkers: 2-5\n"
            "Specialisatie: Verbouw, restauratie, houtwerk\n"
            "Opmerking: 30+ jaar ervaring"
        ),
    },
    {
        "name": "Bouwbedrijf Constantin",
        "address": "Hoogezand",
        "website": "bouwbedrijfconstantin.nl",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Specialisatie: Kozijnen, deuren, renovaties, verbouwingen. 7+ jaar actief",
    },
    {
        "name": "Bouwbedrijf Bé Zwiers B.V.",
        "address": "Kiel-Windeweer",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "KvK: 02077789",
    },
    {
        "name": "Oldenziel Infra",
        "address": "Winkelhoek 58, 9601 EV Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Subcategorie: GWW\nSpecialisatie: Wegenbouw en infrastructuur",
    },
    {
        "name": "Bouw strikt Noord",
        "address": "Herenstraat 61, 9611 BB Sappemeer",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Specialisatie: Bouwbedrijf actief in Noord-Nederland",
    },
    {
        "name": "BEDEKO Betontechnieken B.V.",
        "address": "Sappemeer",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Specialisatie: Betonreparatie, spuitbeton, injecteren, coatings, kelderafdichtingen",
    },
    {
        "name": "Van Delden Bouw B.V.",
        "address": "Dorpsstraat 172, 9605 PE Kiel-Windeweer",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Specialisatie: Aannemersbedrijf",
    },
    {
        "name": "K. Lamein Nieuwbouw & Verbouw",
        "address": "Hoogezand",
        "website": "lameinbouw.nl",
        "email": "",
        "phone": "06-21382806",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 85705632\n"
            "Opgericht: 2022\n"
            "Specialisatie: Hout en beton, hallenbouw"
        ),
    },
    {
        "name": "Wouter Bouw B.V.",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 2023\n"
            "Medewerkers: 5-9"
        ),
    },
    {
        "name": "AG Bouwbedrijf",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 57154392\n"
            "Opgericht: 1970"
        ),
    },
    {
        "name": "Bouwbedrijf Effect",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 58476423\n"
            "Opgericht: 2018"
        ),
    },
    {
        "name": "Bouw & Installatie Smeins ZZP",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 87613808\n"
            "Opgericht: 2022\n"
            "Specialisatie: Bouw en installatie"
        ),
    },
    {
        "name": "Weening Bouw",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 86752448\n"
            "Opgericht: 2022"
        ),
    },
    {
        "name": "Martinus bouwbedrijf",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 85327654\n"
            "Opgericht: 2022"
        ),
    },
    {
        "name": "Adrian Bouw",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 85595519\n"
            "Opgericht: 2022"
        ),
    },
    {
        "name": "WOBIM Bouw en Infra Advies",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 87973111\n"
            "Opgericht: 2022\n"
            "Specialisatie: Bouw- en infra-advies"
        ),
    },
    {
        "name": "Dakdekker Hoogezand",
        "address": "Hoogezand",
        "website": "dakdekkerhoogezand.nl",
        "email": "",
        "phone": "085-0195241",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Specialisatie: Dakdekken\nOpmerking: 30+ jaar ervaring, 24/7 bereikbaar",
    },
]

# ---------------------------------------------------------------------------
# Categorie 2: Installatiebedrijven (19)
# ---------------------------------------------------------------------------
INSTALLATIEBEDRIJVEN = [
    {
        "name": "Installatiebedrijf Mulder Sappemeer B.V.",
        "address": "K. de Haanstraat 47, 9610 AA Sappemeer",
        "website": "muldersappemeer.nl",
        "email": "",
        "phone": "0598-392495",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1925\n"
            "Subcategorie: Totaalinstallateur\n"
            "Specialisatie: CV, sanitair, duurzame energie, luchtbehandeling\n"
            "Opmerking: VCA-gecertificeerd, lid Techniek Nederland"
        ),
    },
    {
        "name": "MG Electro Sappemeer B.V.",
        "address": "Sappemeer",
        "website": "mgelectro.nl",
        "email": "",
        "phone": "0598-392789",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 2001\n"
            "Subcategorie: Elektrotechniek\n"
            "Specialisatie: Krachtstroom, beveiliging, verlichting, duurzame energie\n"
            "Opmerking: Zusterbedrijf Installatiebedrijf Mulder"
        ),
    },
    {
        "name": "P&B Techniek",
        "address": "Slochterstraat 65, 9611 CN Sappemeer",
        "website": "penbtechniek.nl",
        "email": "",
        "phone": "06-52676117",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Totaalinstallateur\n"
            "Specialisatie: Elektra, CV, sanitair, koeltechniek, brandbeveiliging, "
            "datanetwerken\n"
            "Opmerking: 24/7 bereikbaar. Ook: Koeltechniek Midden-Groningen. "
            "Tel. vast: 0598-394949"
        ),
    },
    {
        "name": "MHB Techniek B.V.",
        "address": "Vredenburgweg 7, 9601 KL Hoogezand",
        "website": "mhbtechniek.nl",
        "email": "",
        "phone": "0598-703200",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Duurzame energie\n"
            "Specialisatie: Airco's, zonnepanelen, warmtepompen, laadpalen, "
            "thuisbatterijen, beveiliging"
        ),
    },
    {
        "name": "Vrieswijk Installaties",
        "address": "Julianastraat 17, 9601 LK Hoogezand",
        "website": "installatiebedrijf-hoogezand.nl",
        "email": "",
        "phone": "06-37598318",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Totaalinstallateur\n"
            "Specialisatie: CV, sanitair, airco, domotica, ventilatie\n"
            "Opmerking: 10+ jaar ervaring, 553 Werkspot-reviews"
        ),
    },
    {
        "name": "Reinders Installatietechnieken",
        "address": "Korte Groningerweg 43, 9607 PS Foxhol",
        "website": "reindersfoxhol.nl",
        "email": "",
        "phone": "0598-392263",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1995\n"
            "Subcategorie: Totaalinstallateur\n"
            "Specialisatie: Verwarming/koeling, elektra, dak-/zinkwerk, sanitair\n"
            "Opmerking: Showroom aanwezig"
        ),
    },
    {
        "name": "Installatiebedrijf Pot Slochteren B.V.",
        "address": "Hoofdweg 83-87, 9621 AD Slochteren",
        "website": "potslochteren.nl",
        "email": "",
        "phone": "0598-421495",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1977\n"
            "Medewerkers: 10-19\n"
            "Subcategorie: Totaalinstallateur\n"
            "Specialisatie: Elektro, sanitair, warmtepompen, domotica, wifi\n"
            "Opmerking: Hart werkgebied Midden-Groningen"
        ),
    },
    {
        "name": "GGB Installaties B.V.",
        "address": "Weg der Verenigde Naties 20, 9636 HW Zuidbroek",
        "website": "ggbinstallaties.nl",
        "email": "",
        "phone": "0598-450250",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Medewerkers: ~60\n"
            "Subcategorie: Totaalinstallateur\n"
            "Specialisatie: Woningbouw/utiliteitsbouw\n"
            "Opmerking: KIWA-gecertificeerd, BIM-engineering"
        ),
    },
    {
        "name": "De Wan Elektrotechniek",
        "address": "Sportterreinstraat 110, 9602 EG Hoogezand",
        "website": "de-wan.nl",
        "email": "",
        "phone": "06-50207052",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Elektrotechniek\n"
            "Specialisatie: Verlichting, meterkasten, intercom, domotica, smart home"
        ),
    },
    {
        "name": "MKElektro",
        "address": "Hoogezand-Sappemeer",
        "website": "mkelektro.nl",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 2023\n"
            "Subcategorie: Elektrotechniek\n"
            "Specialisatie: Elektro, beveiliging, camerasystemen, zonnepanelen, "
            "smart home (Gira)"
        ),
    },
    {
        "name": "Hamminga Installatieservice",
        "address": "Hoogezand",
        "website": "hamminga-installatieservice.nl",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: HVAC\n"
            "Specialisatie: Warmtepompen, CV-ketels, airco"
        ),
    },
    {
        "name": "Hoekstra Loodgieters & CV",
        "address": "Cypressenlaan 18, 9603 DG Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 56791291\n"
            "Subcategorie: Loodgieter/CV"
        ),
    },
    {
        "name": "Kerdijk Verwarmings- en Loodgieterswerken",
        "address": "Winkelhoek 41, 9601 EX Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Subcategorie: Loodgieter/verwarming",
    },
    {
        "name": "LS-Installatie",
        "address": "Hoogezand-Sappemeer",
        "website": "ls-installatie.nl",
        "email": "",
        "phone": "06-41612713",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Loodgieter/CV\n"
            "Specialisatie: CV-ketel onderhoud, warmtepompen, badkamers, riool, "
            "storingsdienst"
        ),
    },
    {
        "name": "Yas Installatie",
        "address": "Hoogezand-Sappemeer",
        "website": "yasinstallatie.nl",
        "email": "",
        "phone": "06-43283700",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: HVAC\n"
            "Specialisatie: CV-ketels, airco, warmtepompen\n"
            "Opmerking: 24/7 storingsdienst"
        ),
    },
    {
        "name": "JBP Wildeboer O.V.R.",
        "address": "Foxhol",
        "website": "groningenloodgieter.nl",
        "email": "",
        "phone": "0598-725500",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Loodgieter/dakdekker\n"
            "Opmerking: 30+ jaar ervaring, 24/7 bereikbaar"
        ),
    },
    {
        "name": "Airco Service Sappemeer",
        "address": "Sappemeer",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "KvK: 01130014\n"
            "Opgericht: 2008\n"
            "Subcategorie: Airco\n"
            "Specialisatie: Airco-installatie, onderhoud en reparatie"
        ),
    },
    {
        "name": "Wazo Installateurs B.V.",
        "address": "Woldweg 118, 9606 PH Kropswolde",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Subcategorie: Loodgieter/installateur",
    },
    {
        "name": "Installatiebedrijf Groenewoud B.V.",
        "address": "W.A. Scholtenlaan 11, 9615 TG Kolham",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Subcategorie: Installatiebedrijf",
    },
]

# ---------------------------------------------------------------------------
# Categorie 3: Productie- en maakbedrijven (20)
# ---------------------------------------------------------------------------
PRODUCTIEBEDRIJVEN = [
    {
        "name": "Gieterij Borcherts B.V. (Dekens Groep)",
        "address": "Noorderstraat 370, 9611 AV Sappemeer",
        "website": "dekensmetaalgieterijen.nl",
        "email": "",
        "phone": "0598-392997",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1925\n"
            "Medewerkers: 21-50 (uitbreiding naar 65+ fte)\n"
            "Subcategorie: Metaalgieterij\n"
            "Specialisatie: Lamellair/nodulair gietijzer\n"
            "Opmerking: Onderdeel Dekens Groep"
        ),
    },
    {
        "name": "Pluim Las- en Constructiebedrijf B.V.",
        "address": "Sluiskade 1b, 9601 LA Hoogezand",
        "website": "henkpluim.nl",
        "email": "",
        "phone": "0598-395216",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Medewerkers: 6-10\n"
            "Subcategorie: Las/constructie\n"
            "Specialisatie: Staal, aluminium, RVS. 8.000 m² bedrijfshal\n"
            "Opmerking: ISO, VCA, NEN-EN 1090-2 gecertificeerd"
        ),
    },
    {
        "name": "Lasbedrijf Muntslag",
        "address": "Molenraai 1, 9611 TH Sappemeer",
        "website": "lasbedrijfmuntslag.nl",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Las/constructie\n"
            "Specialisatie: Constructie- en laswerk, RVS/aluminium/staal. "
            "Lasrobot voor kleine series\n"
            "Opmerking: 22+ jaar ervaring"
        ),
    },
    {
        "name": "Venko Straal- en Coatingsbedrijf B.V.",
        "address": "Abramskade 12, 9601 KM Hoogezand",
        "website": "venko.nl",
        "email": "",
        "phone": "0598-394035",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Medewerkers: 6-10\n"
            "Subcategorie: Oppervlaktebehandeling\n"
            "Specialisatie: Stralen, coaten"
        ),
    },
    {
        "name": "Delta North C.V.",
        "address": "Korte Groningerweg, 9607 PS Foxhol",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Leidingbouw\n"
            "Specialisatie: Leidingbouw, constructies en onderhoud"
        ),
    },
    {
        "name": "C.tech Hoogezand",
        "address": "Erasmusweg 51, 9602 AC Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": "Subcategorie: Metaalbewerking",
    },
    {
        "name": "Witting Technische Handelsonderneming B.V.",
        "address": "De Vosholen 99-a, 9611 TE Sappemeer",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Medewerkers: 2-5\n"
            "Subcategorie: Oppervlaktebehandeling\n"
            "Specialisatie: Oppervlaktebehandeling en bekleding van metaal"
        ),
    },
    {
        "name": "Meijer Welding Products",
        "address": "Sluiskade, Hoogezand (Martenshoek)",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Lastechniek\n"
            "Specialisatie: Lasproducten en lastechniek"
        ),
    },
    {
        "name": "Machinefabriek Veldhuis B.V.",
        "address": "Spoorstraat Noord 23, 9601 AX Hoogezand",
        "website": "veldhuisbv.nl",
        "email": "",
        "phone": "0598-393331",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Machinebouw\n"
            "Specialisatie: Machinebouw op maat: ontwerp, productie, montage. "
            "IJkinstallaties, draadsnijmachines, speciaalmachines"
        ),
    },
    {
        "name": "Machinefabriek Börger B.V.",
        "address": "Van Neckstraat 1a, 9601 GW Hoogezand",
        "website": "mf-borger.nl",
        "email": "",
        "phone": "0598-392733",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1945\n"
            "Medewerkers: ~30\n"
            "Subcategorie: Machinebouw\n"
            "Specialisatie: CNC draaien/frezen, constructiewerk, scheepsbouw\n"
            "Opmerking: Full-service machinefabriek"
        ),
    },
    {
        "name": "Scheepswerf Ferus Smit B.V.",
        "address": "Scheepswervenweg 7, 9608 PD Westerbroek",
        "website": "ferussmit.com",
        "email": "",
        "phone": "050-4042555",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Medewerkers: ~200\n"
            "Subcategorie: Scheepsbouw\n"
            "Specialisatie: Vrachtschepen tot 30.000 DWT\n"
            "Opmerking: 100+ jaar historie. Groot bedrijf, vermoedelijk eigen admin/ICT"
        ),
    },
    {
        "name": "Damen Shipyard Hoogezand",
        "address": "Scheepswervenweg 13, 9607 PX Foxhol",
        "website": "schn.nl",
        "email": "",
        "phone": "0598-399450",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Scheepsbouw\n"
            "Specialisatie: Special-purpose schepen\n"
            "Opmerking: Onderdeel Damen Group. Groot concern, vermoedelijk eigen admin/ICT"
        ),
    },
    {
        "name": "Royal Bodewes",
        "address": "Scheepswervenweg 14, Foxhol",
        "website": "",
        "email": "",
        "phone": "0598-4046900",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Scheepsbouw\n"
            "Specialisatie: Scheepsbouw (rompen)"
        ),
    },
    {
        "name": "Pattje Waterhuizen B.V.",
        "address": "Waterhuizen 5, 9609 PA Waterhuizen",
        "website": "pattjewaterhuizen.nl",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Medewerkers: ~60\n"
            "Subcategorie: Scheepsbouw\n"
            "Specialisatie: Support vessels"
        ),
    },
    {
        "name": "Constructiebedrijf Hoogezand B.V.",
        "address": "Scheepswervenweg 11, 9607 PX Foxhol",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Scheepsbouw/constructie\n"
            "Specialisatie: Constructiewerk, scheepsbouw-gerelateerd"
        ),
    },
    {
        "name": "Benes Roer- en Stevenbouw B.V.",
        "address": "Hoogezand",
        "website": "",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Scheepsonderdelen\n"
            "Specialisatie: Roer- en stevenbouw (gespecialiseerde scheepsonderdelen)"
        ),
    },
    {
        "name": "ESKA / Solidus Solutions",
        "address": "Noorderstraat 394, 9611 AW Sappemeer",
        "website": "eska.com",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1879\n"
            "Medewerkers: 350-450\n"
            "Subcategorie: Kartonproductie\n"
            "Specialisatie: Wereldleider massiefkarton. 275.000+ ton/jaar, "
            "100% recycled\n"
            "Opmerking: Zeer groot bedrijf, vermoedelijk eigen admin/ICT"
        ),
    },
    {
        "name": "Hydro Extrusion Hoogezand B.V.",
        "address": "Nijverheidsweg 9, 9601 LX Hoogezand",
        "website": "hydro.com",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Aluminiumextrusie\n"
            "Specialisatie: Aluminium extrusie, anodiseren, poedercoaten\n"
            "Opmerking: Onderdeel Norsk Hydro. Zeer groot concern, "
            "vermoedelijk eigen admin/ICT"
        ),
    },
    {
        "name": "Royal AVEBE",
        "address": "Avebe-weg 1, 9607 PT Foxhol",
        "website": "avebe.com",
        "email": "",
        "phone": "",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Opgericht: 1842\n"
            "Subcategorie: Voedingsmiddelen\n"
            "Specialisatie: Aardappelzetmeel en -derivaten\n"
            "Opmerking: Internationaal coöperatief concern. "
            "Zeer groot bedrijf, vermoedelijk eigen admin/ICT"
        ),
    },
    {
        "name": "BouwCenter Meijer",
        "address": "Korte Groningerweg 31, 9607 PS Foxhol",
        "website": "bouwcentermeijer.nl",
        "email": "",
        "phone": "0598-390899",
        "contact_first_name": "",
        "contact_last_name": "",
        "aanhef": "Geachte heer/mevrouw",
        "notes": (
            "Subcategorie: Houthandel\n"
            "Specialisatie: Houthandel, bouwmaterialen, plaatmaterialen"
        ),
    },
]


class Command(BaseCommand):
    help = "Laad 61 MKB-bedrijven uit Hoogezand-Sappemeer als prospects"

    def handle(self, *args, **options):
        group, created = ProspectGroup.objects.get_or_create(
            slug="mkb-hoogezand-sappemeer",
            defaults={
                "name": "MKB Hoogezand-Sappemeer",
                "description": (
                    "MKB-bedrijven in de regio Hoogezand-Sappemeer: "
                    "bouw, installatie en productie"
                ),
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Groep aangemaakt: {group.name}"))
        else:
            self.stdout.write(f"Groep bestaat al: {group.name}")

        created_count = 0
        skipped_count = 0
        linked_count = 0

        categories = [
            (BOUWBEDRIJVEN, "Bouwbedrijf"),
            (INSTALLATIEBEDRIJVEN, "Installatiebedrijf"),
            (PRODUCTIEBEDRIJVEN, "Productiebedrijf"),
        ]

        for prospects_list, business_type in categories:
            self.stdout.write(f"\n--- {business_type} ---")
            for data in prospects_list:
                existing = find_existing_prospect(data["name"])
                if existing:
                    if not existing.groups.filter(pk=group.pk).exists():
                        existing.groups.add(group)
                        linked_count += 1
                        self.stdout.write(
                            f"  ~ {existing.name} (bestaat al, toegevoegd aan groep)"
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(f"  ~ {existing.name} (bestaat al)")
                else:
                    prospect = Prospect(
                        name=data["name"],
                        address=data["address"],
                        website=data["website"],
                        email=data["email"],
                        phone=data["phone"],
                        contact_first_name=data["contact_first_name"],
                        contact_last_name=data["contact_last_name"],
                        aanhef=data["aanhef"],
                        business_type=business_type,
                        status="new",
                        notes=data["notes"],
                    )
                    prospect.save()
                    prospect.groups.add(group)
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  + {prospect.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nKlaar: {created_count} aangemaakt, {linked_count} gelinkt, "
                f"{skipped_count} overgeslagen"
            )
        )
