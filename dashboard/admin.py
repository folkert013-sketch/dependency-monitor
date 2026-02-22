from django.contrib import admin

from .models import Finding, Report


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
