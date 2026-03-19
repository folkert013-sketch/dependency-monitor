from django.contrib import admin

from .models import (
    BlogArticle, BusinessType, ComplianceReport, ComplianceSection,
    ComplianceSectionVersion, DiaryGoal, Finding, PlacesSearch, Prospect,
    ProspectGroup, ProspectResponse, Report, ResponseTemplate, SalesDiary,
    Team, TeamAgent, TeamTask, TeamVariable, TemplateCategory, TrackingEvent,
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
