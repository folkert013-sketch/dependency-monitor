from django.urls import path

from . import views

app_name = "samenstellen"

urlpatterns = [
    # Overzicht + configuratie
    path("", views.home, name="home"),
    path("fase/<int:pk>/edit/", views.fase_edit, name="fase_edit"),
    path("fase/<int:pk>/koppel/", views.fase_koppel, name="fase_koppel"),
    # Opdrachten
    path("nieuw/", views.opdracht_create, name="opdracht_create"),
    path("<int:pk>/", views.opdracht_detail, name="opdracht_detail"),
    path("<int:pk>/delete/", views.opdracht_delete, name="opdracht_delete"),
    # Uitvoering
    path("<int:pk>/run/<int:run_nr>/", views.opdracht_run, name="opdracht_run"),
    path("<int:pk>/status/", views.opdracht_status, name="opdracht_status"),
    path("<int:pk>/stop/", views.opdracht_stop, name="opdracht_stop"),
    path("<int:pk>/upload-definitief/", views.upload_definitief, name="upload_definitief"),
    # Documenten
    path("<int:pk>/document/upload/", views.document_upload, name="document_upload"),
    path("<int:pk>/document/<int:doc_pk>/delete/", views.document_delete, name="document_delete"),
]
