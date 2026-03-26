from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    # Hub
    path("", views.hub, name="hub"),
    # Dependency Monitor
    path("dependency/", views.dependency_home, name="dependency_home"),
    path("about/", views.about, name="about"),
    path("report/<int:pk>/", views.report_detail, name="report_detail"),
    # Dependency scan
    path("scan/start/", views.start_scan, name="start_scan"),
    path("scan/stop/<int:pk>/", views.stop_scan, name="stop_scan"),
    path("scan/status/<int:pk>/", views.scan_status, name="scan_status"),
    path("scan/logs/<int:pk>/", views.scan_logs, name="scan_logs"),
    # Fiscal / Bedrijfsmonitor
    path("bedrijfsmonitor/", views.fiscal_home, name="fiscal_home"),
    path("bedrijfsmonitor/artikel/<slug:slug>/", views.article_detail, name="article_detail"),
    path("bedrijfsmonitor/onderzoek/start/", views.start_fiscal_research, name="start_fiscal_research"),
    path("bedrijfsmonitor/onderzoek/stop/<int:pk>/", views.stop_fiscal_research, name="stop_fiscal_research"),
    path("bedrijfsmonitor/onderzoek/status/<int:pk>/", views.fiscal_research_status, name="fiscal_research_status"),
    # HTMX partials
    path("htmx/report-list/", views.htmx_report_list, name="htmx_report_list"),
    path("htmx/report-card/<int:pk>/", views.htmx_report_card, name="htmx_report_card"),
    path("htmx/finding/<int:pk>/", views.htmx_finding_detail, name="htmx_finding_detail"),
    path("htmx/article-list/", views.htmx_article_list, name="htmx_article_list"),
    # --- AI Configuration ---
    path("ai-config/", views.ai_config, name="ai_config"),
    # --- Team Builder ---
    path("teams/", views.team_list, name="team_list"),
    path("ai-teams/", views.team_list, name="ai_teams"),  # backward compat alias
    path("teams/new/", views.team_create, name="team_create"),
    path("teams/bulk-delete/", views.team_bulk_delete, name="team_bulk_delete"),
    path("teams/<slug:slug>/", views.team_detail, name="team_detail"),
    path("teams/<slug:slug>/delete/", views.team_delete, name="team_delete"),
    path("teams/<slug:slug>/update/", views.team_update, name="team_update"),
    # Team agents
    path("teams/<slug:slug>/agents/add/", views.team_agent_add, name="team_agent_add"),
    path("teams/<slug:slug>/agents/<int:pk>/edit/", views.team_agent_edit, name="team_agent_edit"),
    path("teams/<slug:slug>/agents/<int:pk>/delete/", views.team_agent_delete, name="team_agent_delete"),
    path("teams/<slug:slug>/agents/<int:pk>/set-manager/", views.team_agent_set_manager, name="team_agent_set_manager"),
    # Team tasks
    path("teams/<slug:slug>/tasks/add/", views.team_task_add, name="team_task_add"),
    path("teams/<slug:slug>/tasks/<int:pk>/edit/", views.team_task_edit, name="team_task_edit"),
    path("teams/<slug:slug>/tasks/<int:pk>/delete/", views.team_task_delete, name="team_task_delete"),
    # Team variables
    path("teams/<slug:slug>/variables/add/", views.team_variable_add, name="team_variable_add"),
    path("teams/<slug:slug>/variables/<int:pk>/edit/", views.team_variable_edit, name="team_variable_edit"),
    path("teams/<slug:slug>/variables/<int:pk>/delete/", views.team_variable_delete, name="team_variable_delete"),
    path("teams/<slug:slug>/variables/<int:pk>/upload/", views.team_variable_upload, name="team_variable_upload"),
    # Team run
    path("teams/<slug:slug>/run/", views.team_run, name="team_run"),
    path("teams/<slug:slug>/run/status/<int:pk>/", views.team_run_status, name="team_run_status"),
    path("teams/<slug:slug>/run/stop/<int:pk>/", views.team_run_stop, name="team_run_stop"),
    path("teams/<slug:slug>/run/<int:pk>/pdf/", views.team_run_pdf, name="team_run_pdf"),
    path("teams/<slug:slug>/run/dismiss/<int:pk>/", views.team_run_dismiss, name="team_run_dismiss"),
    # WWFT Compliance
    path("compliance/", views.compliance_home, name="compliance_home"),
    path("compliance/sectie/nieuw/", views.compliance_section_add, name="compliance_section_add"),
    path("compliance/sectie/<str:key>/edit/", views.compliance_section_edit, name="compliance_section_edit"),
    path("compliance/sectie/<str:key>/edit-form/", views.compliance_section_edit_form, name="compliance_section_edit_form"),
    path("compliance/sectie/<str:key>/card/", views.compliance_section_card, name="compliance_section_card"),
    path("compliance/sectie/<str:key>/check/", views.compliance_section_check, name="compliance_section_check"),
    path("compliance/sectie/<str:key>/status/<int:pk>/", views.compliance_section_status, name="compliance_section_status"),
    path("compliance/sectie/<str:key>/stop/<int:pk>/", views.compliance_section_stop, name="compliance_section_stop"),
    path("compliance/wetgeving/zoeken/", views.compliance_legislation_search, name="compliance_legislation_search"),
    # Compliance investigation
    path("compliance/onderzoek/", views.compliance_investigate, name="compliance_investigate"),
    path("compliance/onderzoek/status/<int:pk>/", views.compliance_investigate_status, name="compliance_investigate_status"),
    path("compliance/onderzoek/stop/<int:pk>/", views.compliance_investigate_stop, name="compliance_investigate_stop"),
    # Compliance archive
    path("compliance/archief/", views.compliance_archive, name="compliance_archive"),
    path("compliance/archief/<int:pk>/", views.compliance_report_detail, name="compliance_report_detail"),
    # Sales / CRM
    path("sales/", views.sales_home, name="sales_home"),
    path("sales/kaart/", views.sales_map, name="sales_map"),
    path("sales/zoeken/", views.sales_search, name="sales_search"),
    path("sales/groepen/nieuw/", views.prospect_group_create, name="prospect_group_create"),
    path("sales/groepen/<slug:slug>/", views.prospect_group_detail, name="prospect_group_detail"),
    path("sales/groepen/<slug:slug>/edit/", views.prospect_group_edit, name="prospect_group_edit"),
    path("sales/groepen/<slug:slug>/delete/", views.prospect_group_delete, name="prospect_group_delete"),
    # Bulk Email
    path("sales/email/preview/", views.bulk_email_preview, name="bulk_email_preview"),
    path("sales/email/preview/<slug:slug>/", views.bulk_email_prospect_preview, name="bulk_email_prospect_preview"),
    path("htmx/sales/email/test/", views.htmx_send_test_email, name="htmx_send_test_email"),
    path("htmx/sales/email/send/", views.htmx_bulk_email_send, name="htmx_bulk_email_send"),
    # Response Templates
    path("sales/templates/", views.sales_templates, name="sales_templates"),
    path("sales/templates/nieuw/", views.response_template_create, name="response_template_create"),
    path("sales/templates/reorder/", views.response_template_reorder, name="response_template_reorder"),
    path("sales/templates/<int:pk>/move/<str:direction>/", views.response_template_move, name="response_template_move"),
    path("sales/templates/<slug:slug>/preview/", views.response_template_preview, name="response_template_preview"),
    path("sales/templates/<slug:slug>/edit/", views.response_template_edit, name="response_template_edit"),
    path("sales/templates/<slug:slug>/delete/", views.response_template_delete, name="response_template_delete"),
    path("sales/templates/<slug:slug>/star/", views.response_template_toggle_star, name="response_template_toggle_star"),
    # Template Categories
    path("sales/templates/categories/add/", views.template_category_add, name="template_category_add"),
    path("sales/templates/categories/<int:pk>/edit/", views.template_category_edit, name="template_category_edit"),
    path("sales/templates/categories/<int:pk>/delete/", views.template_category_delete, name="template_category_delete"),
    path("sales/templates/<int:pk>/set-category/", views.htmx_template_set_category, name="template_set_category"),
    # Sales Diary
    path("sales/dagboek/", views.sales_diary, name="sales_diary"),
    path("sales/dagboek/<str:date>/", views.sales_diary_edit, name="sales_diary_edit"),
    path("htmx/sales/dagboek/<str:date>/delete/", views.htmx_sales_diary_delete, name="htmx_sales_diary_delete"),
    # HTMX partials for Sales
    path("htmx/sales/geocode-all/", views.htmx_geocode_prospects, name="htmx_geocode_prospects"),
    path("htmx/sales/search-results/", views.htmx_sales_search_results, name="htmx_sales_search_results"),
    path("htmx/sales/internal-search/", views.htmx_internal_prospect_search, name="htmx_internal_prospect_search"),
    path("htmx/sales/prospect/<slug:slug>/popup/", views.htmx_prospect_popup, name="htmx_prospect_popup"),
    path("htmx/sales/prospect/<slug:slug>/status/", views.htmx_prospect_status, name="htmx_prospect_status"),
    path("htmx/sales/prospect/save/", views.htmx_prospect_save, name="htmx_prospect_save"),
    path("htmx/sales/prospect/save-all/", views.htmx_prospect_save_all, name="htmx_prospect_save_all"),
    path("htmx/sales/prospect/bulk-update/", views.htmx_prospect_bulk_update, name="htmx_prospect_bulk_update"),
    path("htmx/sales/prospect/bulk-delete/", views.htmx_prospect_bulk_delete, name="htmx_prospect_bulk_delete"),
    path("htmx/sales/prospect/check-duplicate/", views.htmx_prospect_check_duplicate, name="htmx_prospect_check_duplicate"),
    path("htmx/sales/prospect/manual-add/", views.htmx_prospect_manual_add, name="htmx_prospect_manual_add"),
    path("htmx/sales/prospect/link-group/", views.htmx_prospect_link_to_group, name="htmx_prospect_link_to_group"),
    path("htmx/sales/prospect/<slug:slug>/response/", views.htmx_prospect_response, name="htmx_prospect_response"),
    path("htmx/sales/prospect/<slug:slug>/scrape-email/", views.htmx_prospect_scrape_email, name="htmx_prospect_scrape_email"),
    path("htmx/sales/prospect/<slug:slug>/delete/", views.htmx_prospect_delete, name="htmx_prospect_delete"),
    # Business Types
    path("sales/business-types/", views.business_types_manage, name="business_types_manage"),
    path("htmx/sales/business-type/add/", views.htmx_business_type_add, name="htmx_business_type_add"),
    path("htmx/sales/business-type/<int:pk>/delete/", views.htmx_business_type_delete, name="htmx_business_type_delete"),
    # Vacancy scraping (within Sales)
    path("sales/vacatures/", views.vacancy_search, name="vacancy_search"),
    path("sales/vacatures/analyse/", views.vacancy_analysis, name="vacancy_analysis"),
    path("htmx/vacatures/results/", views.htmx_vacancy_results, name="htmx_vacancy_results"),
    path("htmx/vacatures/save-company/", views.htmx_vacancy_save_company, name="htmx_vacancy_save_company"),
    path("htmx/vacatures/save-all/", views.htmx_vacancy_save_all, name="htmx_vacancy_save_all"),
    # Email tracking (public, no login)
    path("t/o/<uuid:token>/", views.track_open, name="track_open"),
    path("t/c/<uuid:token>/", views.track_click, name="track_click"),
]
