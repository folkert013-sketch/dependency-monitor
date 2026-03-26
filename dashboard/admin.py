from django.contrib import admin

from .models import (
    BlogArticle, BusinessType, ComplianceReport, ComplianceSection,
    ComplianceSectionVersion, DiaryGoal, Finding,
    FiscaalArtikel, FiscaalConceptMapping, FiscaalHoofdstuk, FiscaalLid, FiscaleWet,
    PlacesSearch, Prospect,
    ProspectGroup, ProspectResponse, Report, ResponseTemplate,
    RJAlinea, RJHoofdstuk, RJRubriekMapping, RJSectie,
    SalesDiary, Team, TeamAgent, TeamTask, TeamVariable,
    TemplateCategory, TrackingEvent,
    VpbBoekHoofdstuk, VpbBoekPassage, VpbBoekSectie,
)


class FindingInline(admin.TabularInline):
    model = Finding
    extra = 0


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["created_at", "status", "total_dependencies", "vulnerability_count", "action_required"]
    list_filter = ["status", "action_required"]
    inlines = [FindingInline]


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ["package_name", "severity", "category", "current_version", "latest_version"]
    list_filter = ["severity", "category"]


@admin.register(BlogArticle)
class BlogArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "status", "quality_score", "created_at"]
    list_filter = ["status", "category"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "intro", "body"]


# --- Team Builder ---

class TeamVariableInline(admin.TabularInline):
    model = TeamVariable
    extra = 0


class TeamAgentInline(admin.TabularInline):
    model = TeamAgent
    extra = 0


class TeamTaskInline(admin.TabularInline):
    model = TeamTask
    extra = 0


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "process", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TeamVariableInline, TeamAgentInline, TeamTaskInline]


class ComplianceSectionVersionInline(admin.TabularInline):
    model = ComplianceSectionVersion
    extra = 0
    readonly_fields = ["body", "changed_by", "created_at"]


@admin.register(ComplianceSection)
class ComplianceSectionAdmin(admin.ModelAdmin):
    list_display = ["key", "title", "status", "can_ai_update", "last_checked", "order"]
    list_filter = ["status", "can_ai_update", "office_action_required"]
    list_editable = ["order", "can_ai_update"]
    search_fields = ["title", "body"]
    inlines = [ComplianceSectionVersionInline]


@admin.register(ComplianceSectionVersion)
class ComplianceSectionVersionAdmin(admin.ModelAdmin):
    list_display = ["section", "changed_by", "created_at"]
    list_filter = ["changed_by"]
    readonly_fields = ["section", "body", "changed_by", "created_at"]


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ["created_at", "report_type", "entity_name", "risk_level"]
    list_filter = ["report_type", "risk_level"]
    search_fields = ["entity_name", "summary"]


# --- Sales / CRM ---

@admin.register(ProspectGroup)
class ProspectGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "status", "contact_channel", "google_rating", "created_at"]
    list_filter = ["status", "contact_channel"]
    search_fields = ["name", "email", "address", "phone", "website"]
    prepopulated_fields = {"slug": ("name",)}


class DiaryGoalInline(admin.TabularInline):
    model = DiaryGoal
    extra = 1


@admin.register(SalesDiary)
class SalesDiaryAdmin(admin.ModelAdmin):
    list_display = ["date", "updated_at"]
    list_filter = ["date"]
    search_fields = ["results", "notes"]
    inlines = [DiaryGoalInline]


@admin.register(PlacesSearch)
class PlacesSearchAdmin(admin.ModelAdmin):
    list_display = ["query", "location", "radius_km", "results_count", "created_at"]
    search_fields = ["query", "location"]


@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "order"]
    list_editable = ["order", "color"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ResponseTemplate)
class ResponseTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "subject", "category", "order", "updated_at"]
    list_filter = ["category"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "subject", "body"]


class ProspectResponseInline(admin.TabularInline):
    model = ProspectResponse
    extra = 0
    readonly_fields = ["sent_at"]


@admin.register(ProspectResponse)
class ProspectResponseAdmin(admin.ModelAdmin):
    list_display = ["prospect", "template", "sent_at"]
    list_filter = ["template"]
    search_fields = ["prospect__name", "notes"]


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ["token", "event_type", "url", "created_at"]
    list_filter = ["event_type"]
    search_fields = ["token"]
    readonly_fields = ["token", "event_type", "url", "created_at"]
    date_hierarchy = "created_at"


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ["google_type", "label"]
    search_fields = ["google_type", "label"]


# ---------------------------------------------------------------------------
# RJ Richtlijnen
# ---------------------------------------------------------------------------

class RJSectieInline(admin.TabularInline):
    model = RJSectie
    extra = 0
    fields = ["paragraaf", "titel", "order"]


class RJAlineaInline(admin.TabularInline):
    model = RJAlinea
    extra = 0
    fields = ["nummer", "sub_onderwerp", "inhoud", "order"]
    readonly_fields = []


@admin.register(RJHoofdstuk)
class RJHoofdstukAdmin(admin.ModelAdmin):
    list_display = ["code", "titel", "afdeling", "editie", "is_active", "order"]
    list_filter = ["afdeling", "is_active"]
    search_fields = ["code", "titel", "beschrijving"]
    inlines = [RJSectieInline]


@admin.register(RJSectie)
class RJSectieAdmin(admin.ModelAdmin):
    list_display = ["paragraaf", "hoofdstuk", "titel"]
    list_filter = ["hoofdstuk"]
    search_fields = ["paragraaf", "titel"]
    inlines = [RJAlineaInline]


@admin.register(RJAlinea)
class RJAlineaAdmin(admin.ModelAdmin):
    list_display = ["referentie", "sub_onderwerp", "short_inhoud"]
    list_filter = ["sectie__hoofdstuk"]
    search_fields = ["nummer", "inhoud", "sub_onderwerp"]

    @admin.display(description="Referentie")
    def referentie(self, obj):
        return f"{obj.sectie.paragraaf}.{obj.nummer}"

    @admin.display(description="Inhoud")
    def short_inhoud(self, obj):
        return obj.inhoud[:120] + "..." if len(obj.inhoud) > 120 else obj.inhoud


@admin.register(RJRubriekMapping)
class RJRubriekMappingAdmin(admin.ModelAdmin):
    list_display = ["rubriek_naam", "rubriek_code"]
    search_fields = ["rubriek_naam"]
    filter_horizontal = ["hoofdstukken"]


# ---------------------------------------------------------------------------
# Fiscale Wetgeving
# ---------------------------------------------------------------------------

class FiscaalHoofdstukInline(admin.TabularInline):
    model = FiscaalHoofdstuk
    extra = 0
    fields = ["nummer", "titel", "order"]


class FiscaalArtikelInline(admin.TabularInline):
    model = FiscaalArtikel
    extra = 0
    fields = ["nummer", "titel", "is_vervallen", "order"]


class FiscaalLidInline(admin.TabularInline):
    model = FiscaalLid
    extra = 0
    fields = ["nummer", "inhoud", "order"]


@admin.register(FiscaleWet)
class FiscaleWetAdmin(admin.ModelAdmin):
    list_display = ["code", "afkorting", "naam", "bwb_id", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "naam", "afkorting"]
    inlines = [FiscaalHoofdstukInline]


@admin.register(FiscaalHoofdstuk)
class FiscaalHoofdstukAdmin(admin.ModelAdmin):
    list_display = ["nummer", "wet", "titel"]
    list_filter = ["wet"]
    search_fields = ["nummer", "titel"]
    inlines = [FiscaalArtikelInline]


@admin.register(FiscaalArtikel)
class FiscaalArtikelAdmin(admin.ModelAdmin):
    list_display = ["referentie_display", "titel", "is_vervallen"]
    list_filter = ["hoofdstuk__wet", "is_vervallen"]
    search_fields = ["nummer", "titel", "volledige_tekst"]
    inlines = [FiscaalLidInline]

    @admin.display(description="Referentie")
    def referentie_display(self, obj):
        return obj.referentie


@admin.register(FiscaalLid)
class FiscaalLidAdmin(admin.ModelAdmin):
    list_display = ["referentie_display", "short_inhoud"]
    list_filter = ["artikel__hoofdstuk__wet"]
    search_fields = ["nummer", "inhoud"]

    @admin.display(description="Referentie")
    def referentie_display(self, obj):
        return obj.referentie

    @admin.display(description="Inhoud")
    def short_inhoud(self, obj):
        return obj.inhoud[:120] + "..." if len(obj.inhoud) > 120 else obj.inhoud


@admin.register(FiscaalConceptMapping)
class FiscaalConceptMappingAdmin(admin.ModelAdmin):
    list_display = ["concept_naam", "trefwoorden_kort"]
    search_fields = ["concept_naam", "trefwoorden"]
    filter_horizontal = ["artikelen"]

    @admin.display(description="Trefwoorden")
    def trefwoorden_kort(self, obj):
        return obj.trefwoorden[:80] + "..." if len(obj.trefwoorden) > 80 else obj.trefwoorden


# ---------------------------------------------------------------------------
# VPB Boek
# ---------------------------------------------------------------------------

class VpbBoekSectieInline(admin.TabularInline):
    model = VpbBoekSectie
    extra = 0
    fields = ["paragraaf", "titel", "order"]


class VpbBoekPassageInline(admin.TabularInline):
    model = VpbBoekPassage
    extra = 0
    fields = ["volgnummer", "inhoud", "pagina_start", "order"]


@admin.register(VpbBoekHoofdstuk)
class VpbBoekHoofdstukAdmin(admin.ModelAdmin):
    list_display = ["nummer", "titel", "order"]
    search_fields = ["nummer", "titel"]
    inlines = [VpbBoekSectieInline]


@admin.register(VpbBoekSectie)
class VpbBoekSectieAdmin(admin.ModelAdmin):
    list_display = ["paragraaf", "hoofdstuk", "titel"]
    list_filter = ["hoofdstuk"]
    search_fields = ["paragraaf", "titel"]
    inlines = [VpbBoekPassageInline]


@admin.register(VpbBoekPassage)
class VpbBoekPassageAdmin(admin.ModelAdmin):
    list_display = ["sectie", "volgnummer", "pagina_start", "short_inhoud"]
    list_filter = ["sectie__hoofdstuk"]
    search_fields = ["inhoud"]

    @admin.display(description="Inhoud")
    def short_inhoud(self, obj):
        return obj.inhoud[:120] + "..." if len(obj.inhoud) > 120 else obj.inhoud
