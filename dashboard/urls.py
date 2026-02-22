from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("report/<int:pk>/", views.report_detail, name="report_detail"),
    # HTMX partials
    path("htmx/report-list/", views.htmx_report_list, name="htmx_report_list"),
    path("htmx/report-card/<int:pk>/", views.htmx_report_card, name="htmx_report_card"),
    path("htmx/finding/<int:pk>/", views.htmx_finding_detail, name="htmx_finding_detail"),
]
