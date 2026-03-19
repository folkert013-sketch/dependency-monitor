import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .models import EmailSettings
from .services.email_backend import test_connection_from_settings


@login_required
def profile(request):
    email_settings, _ = EmailSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form_type = request.POST.get("form_type", "")

        if form_type == "email_settings":
            email_settings.smtp_user = request.POST.get("smtp_user", "").strip()
            email_settings.display_name = request.POST.get("display_name", "").strip()
            email_settings.graph_tenant_id = request.POST.get("graph_tenant_id", "").strip() or email_settings.graph_tenant_id
            email_settings.graph_client_id = request.POST.get("graph_client_id", "").strip() or email_settings.graph_client_id
            raw_secret = request.POST.get("graph_client_secret", "").strip()
            if raw_secret:
                email_settings.graph_client_secret = raw_secret
            email_settings.save()
            messages.success(request, "E-mail instellingen opgeslagen.")
            return redirect("account_profile")

        # Default: profile info
        user = request.user
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.email = request.POST.get("email", "").strip()
        user.save(update_fields=["first_name", "last_name", "email"])
        messages.success(request, "Gegevens bijgewerkt.")
        return redirect("account_profile")

    return render(request, "registration/profile.html", {
        "email_settings": email_settings,
    })


@login_required
def htmx_email_test(request):
    """Test Graph API connection with stored EmailSettings."""
    if request.method != "POST":
        return redirect("account_profile")
    try:
        es = EmailSettings.objects.get(user=request.user)
    except EmailSettings.DoesNotExist:
        return _email_toast(HttpResponse(""), "error", "Geen e-mail instellingen gevonden.")

    if not es.is_configured:
        return _email_toast(HttpResponse(""), "error", "Vul eerst alle Graph API velden en het e-mailadres in.")

    try:
        test_connection_from_settings(es)
        return _email_toast(HttpResponse(""), "success", "Verbinding geslaagd!")
    except Exception as e:
        return _email_toast(HttpResponse(""), "error", f"Verbinding mislukt: {e}")


def _email_toast(response, toast_type, message):
    response["HX-Trigger"] = json.dumps({"showToast": {"type": toast_type, "message": message}})
    return response


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("account_profile")

    def form_valid(self, form):
        messages.success(self.request, "Wachtwoord succesvol gewijzigd.")
        return super().form_valid(form)
