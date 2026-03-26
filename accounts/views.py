import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
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


@login_required
def api_usage_analytics(request):
    """API usage analytics page — token usage, costs, and breakdown."""
    from dashboard.models import APIUsageLog

    # Filters
    days_param = request.GET.get("days", "30")
    days = int(days_param) if days_param.isdigit() else 0
    service_filter = request.GET.get("service", "")

    qs = APIUsageLog.objects.all()
    if days == 1:
        # "Vandaag" — filter from midnight today
        cutoff = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        qs = qs.filter(created_at__gte=cutoff)
    elif days > 0:
        cutoff = timezone.now() - timedelta(days=days)
        qs = qs.filter(created_at__gte=cutoff)
    if service_filter:
        qs = qs.filter(service=service_filter)

    # Aggregations
    totals = qs.aggregate(
        total_cost=Sum("estimated_cost"),
        total_tokens=Sum("total_tokens"),
        total_calls=Count("id"),
        total_input=Sum("input_tokens"),
        total_output=Sum("output_tokens"),
    )
    # Ensure defaults
    for key in totals:
        if totals[key] is None:
            totals[key] = 0

    # Current month cost (always unfiltered by days/service)
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_cost = APIUsageLog.objects.filter(
        created_at__gte=month_start
    ).aggregate(cost=Sum("estimated_cost"))["cost"] or 0

    # Per-service breakdown
    by_service = list(
        qs.values("service").annotate(
            cost=Sum("estimated_cost"),
            tokens=Sum("total_tokens"),
            calls=Count("id"),
        ).order_by("-cost")
    )
    # Add display names
    service_map = dict(APIUsageLog.SERVICE_CHOICES)
    total_cost_val = float(totals["total_cost"] or 0)
    for entry in by_service:
        entry["display"] = service_map.get(entry["service"], entry["service"])
        entry["pct"] = round(float(entry["cost"] or 0) / total_cost_val * 100) if total_cost_val > 0 else 0

    # Daily trend data (for Chart.js) — include days with zero usage
    daily_qs = (
        qs.values(day=TruncDate("created_at"))
        .annotate(cost=Sum("estimated_cost"))
        .order_by("day")
    )
    daily_map = {d["day"]: float(d["cost"] or 0) for d in daily_qs}

    # Build complete date range including today
    today = timezone.now().date()
    if days > 0:
        start_date = (timezone.now() - timedelta(days=days)).date()
    elif daily_map:
        start_date = min(daily_map.keys())
    else:
        start_date = today

    chart_labels = []
    chart_costs = []
    current = start_date
    while current <= today:
        chart_labels.append(current.strftime("%d %b"))
        chart_costs.append(daily_map.get(current, 0))
        current += timedelta(days=1)

    # Recent logs (paginated)
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page", 1))

    context = {
        "totals": totals,
        "month_cost": month_cost,
        "by_service": by_service,
        "chart_labels": json.dumps(chart_labels),
        "chart_costs": json.dumps(chart_costs),
        "logs": page,
        "days": days,
        "service_filter": service_filter,
        "service_choices": APIUsageLog.SERVICE_CHOICES,
    }

    if getattr(request, "htmx", False):
        return render(request, "registration/_api_usage_table.html", context)

    return render(request, "registration/api_usage.html", context)
