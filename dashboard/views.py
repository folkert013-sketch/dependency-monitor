import atexit
import json
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import close_old_connections, models as db_models, transaction
from django.db.models import Count, Exists, Max, OuterRef, Q
from django.db.models.functions import Lower
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape as html_escape
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .models import (
    _save_with_unique_slug,
    BlogArticle, BusinessType, ComplianceReport, ComplianceSection,
    ComplianceSectionVersion, DiaryGoal, Finding, PlacesSearch, Prospect,
    ProspectGroup, ProspectResponse, Report, ResponseTemplate, SalesDiary,
    ScanJob, ScanLog, TaskOutput, Team, TeamAgent, TeamTask, TeamVariable,
    TemplateCategory, TrackingEvent, Vacancy, VacancySearch,
)
from .services.email_scraper import scrape_contact_info
from .services.google_places import GooglePlacesService
from .services.prospect_dedup import find_existing_prospect
from .services.vacancy_monitor import VacancyMonitorService

_stdout_lock = threading.Lock()
logger = logging.getLogger(__name__)

# K3: Limit concurrent background crew runs (prevents unbounded thread creation)
_scan_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="crew-worker")
atexit.register(_scan_executor.shutdown, wait=True)


def _safe_int(value, default: int) -> int:
    """Convert value to int, returning default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _toast_response(response, toast_type, message):
    """Add HX-Trigger header that fires a showToast event on the client."""
    response["HX-Trigger"] = json.dumps({"showToast": {"type": toast_type, "message": message}})
    return response


def about(request):
    return render(request, "dashboard/about.html")


def hub(request):
    return render(request, "dashboard/hub.html")


def dependency_home(request):
    status_filter = request.GET.get("status", "")
    reports = Report.objects.all()
    if status_filter:
        reports = reports.filter(status=status_filter)

    # B2: Paginate reports
    paginator = Paginator(reports, 20)
    page = request.GET.get("page")
    reports_page = paginator.get_page(page)

    # Check if a dependency scan is currently running
    active_job = ScanJob.objects.filter(status__in=["pending", "running"], job_type="dependency").first()

    if request.htmx:
        return render(request, "dashboard/_report_list.html", {"reports": reports_page, "status_filter": status_filter})

    return render(request, "dashboard/dependency/home.html", {
        "reports": reports_page,
        "status_filter": status_filter,
        "active_job": active_job,
        "active_job_logs": active_job.logs.all() if active_job else [],
    })


def report_detail(request, pk):
    report = get_object_or_404(Report, pk=pk)
    return render(request, "dashboard/report_detail.html", {"report": report})


@ratelimit(key="user_or_ip", rate="3/h", method="POST", block=True)
@require_POST
def start_scan(request):
    """Start a new dependency scan in a background thread."""
    with transaction.atomic():
        active = ScanJob.objects.select_for_update().filter(
            status__in=["pending", "running"], job_type="dependency"
        ).first()
        if active:
            return render(request, "dashboard/_scan_status.html", {"job": active, "logs": active.logs.all()})

        # Link to the seeded team if it exists
        dep_team = Team.objects.filter(slug="dependency-monitor").first()
        job = ScanJob.objects.create(
            status="pending",
            progress_message="Scan wordt gestart...",
            team=dep_team,
        )

    _scan_executor.submit(_run_scan_background, job.pk)

    return render(request, "dashboard/_scan_status.html", {"job": job, "logs": []})


@require_POST
def stop_scan(request, pk):
    """Stop a running dependency scan."""
    job = get_object_or_404(ScanJob, pk=pk)
    if job.status in ("pending", "running"):
        job.status = "failed"
        job.progress_message = "Scan handmatig gestopt"
        job.finished_at = timezone.now()
        job.save()
        ScanLog.objects.create(
            job=job, event_type="error", agent_name="System",
            message="Scan gestopt door gebruiker",
        )
    response = render(request, "dashboard/_scan_status.html", {"job": job, "logs": job.logs.all()})
    return _toast_response(response, "warning", "Scan gestopt")


def scan_status(request, pk):
    """HTMX polling endpoint for scan progress."""
    job = get_object_or_404(ScanJob, pk=pk)
    logs = job.logs.all()

    stale = False
    last_activity_seconds = None
    if job.status == "running":
        last_log = logs.order_by("-created_at").first()
        if last_log:
            last_activity_seconds = int((timezone.now() - last_log.created_at).total_seconds())
            if last_activity_seconds > 600:
                stale = True

    return render(request, "dashboard/_scan_status.html", {
        "job": job,
        "logs": logs,
        "stale": stale,
        "last_activity_seconds": last_activity_seconds,
    })


def scan_logs(request, pk):
    """HTMX polling endpoint for new log entries."""
    job = get_object_or_404(ScanJob, pk=pk)
    after = request.GET.get("after", "0")
    try:
        after_id = int(after)
    except ValueError:
        after_id = 0
    new_logs = job.logs.filter(pk__gt=after_id)
    return render(request, "dashboard/_scan_logs.html", {"logs": new_logs, "job": job})


def htmx_report_list(request):
    status_filter = request.GET.get("status", "")
    reports = Report.objects.all()
    if status_filter:
        reports = reports.filter(status=status_filter)
    paginator = Paginator(reports, 20)
    reports_page = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/_report_list.html", {"reports": reports_page, "status_filter": status_filter})


def htmx_report_card(request, pk):
    report = get_object_or_404(Report, pk=pk)
    return render(request, "dashboard/_report_card.html", {"report": report})


def htmx_finding_detail(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    return render(request, "dashboard/_finding_detail.html", {"finding": finding})


# --- Background scan logic ---

def _run_scan_background(job_pk: int):
    """Runs the CrewAI crew in a background thread and saves results."""
    try:
        import django
        django.setup()
    except Exception:
        logger.error("django.setup() failed in _run_scan_background", exc_info=True)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dashboard_scanjob SET status='failed', error_message='Django setup failed' WHERE id=%s",
                    [job_pk],
                )
        except Exception:
            pass
        return

    close_old_connections()
    from dashboard.models import Finding, Report, ScanJob, ScanLog

    job = ScanJob.objects.get(pk=job_pk)
    job.status = "running"
    job.progress_message = "Agents worden opgestart..."
    job.active_agent = "Dependency Scanner"
    job.tasks_completed = 0
    job.token_count = 0
    job.save(update_fields=["status", "progress_message", "active_agent", "tasks_completed", "token_count"])

    requirements_path = str(Path(settings.MONITORED_PROJECT_PATH) / "requirements.txt")

    def _is_cancelled():
        """Check if the job has been cancelled by the user."""
        try:
            return ScanJob.objects.filter(pk=job_pk, status="failed").exists()
        except Exception:
            return False

    def log_callback(event_type, agent_name, message):
        """Write a log entry to the database."""
        try:
            # Check if cancelled
            if _is_cancelled():
                return
            ScanLog.objects.create(
                job_id=job_pk,
                event_type=event_type,
                agent_name=agent_name or "",
                message=message or "",
            )
            # Update the progress message to the latest meaningful event
            if event_type in ("agent", "task_done", "start"):
                short = (message or "")[:295]
                ScanJob.objects.filter(pk=job_pk).update(progress_message=short)
        except Exception:
            logger.error("Error in scan log_callback", exc_info=True)

    try:
        log_callback("start", "System", "Scan gestart — requirements.txt wordt gelezen...")

        from monitor.run import run_crew
        results = run_crew(requirements_path, log_callback=log_callback, job_pk=job_pk)

        # Create Report
        report = Report.objects.create(
            status=results["status"],
            total_dependencies=results["total_dependencies"],
            outdated_count=results["outdated_count"],
            vulnerability_count=results["vulnerability_count"],
            action_required=results["status"] in ("critical", "warning"),
            tip_of_the_week=results["tip_of_the_week"],
            quote_of_the_week=results["quote_of_the_week"],
            total_tokens=results["total_tokens"],
            estimated_cost=results["estimated_cost"],
            raw_output={
                "raw": results["raw_output"][:50000],
                "findings_count": len(results["findings"]),
            },
        )

        for finding_data in results["findings"]:
            Finding.objects.create(
                report=report,
                severity=finding_data.get("severity", "info"),
                category=finding_data.get("category", "outdated"),
                package_name=finding_data.get("package_name", "Unknown"),
                current_version=finding_data.get("current_version", ""),
                latest_version=finding_data.get("latest_version", ""),
                summary=finding_data.get("summary", ""),
                action_steps=finding_data.get("action_steps", ""),
            )

        job.status = "completed"
        job.report = report
        job.progress_message = f"Scan afgerond — {report.get_status_display()}"
        job.active_agent = ""
        job.tasks_completed = 5
        job.token_count = results["total_tokens"]
        job.finished_at = timezone.now()
        job.save()
        log_callback("result", "System", f"Scan afgerond — status: {report.get_status_display()}")

    except Exception as e:
        logger.error("Dependency scan failed (job=%s)", job_pk, exc_info=True)
        job.status = "failed"
        logger.exception("Job %s failed", job.pk)
        job.error_message = "Er is een fout opgetreden. Controleer de logs voor details."
        job.progress_message = "Scan mislukt"
        job.finished_at = timezone.now()
        job.save()
        log_callback("error", "System", f"Scan mislukt: {type(e).__name__}")
    finally:
        close_old_connections()


# --- Fiscal / Bedrijfsmonitor views ---

def fiscal_home(request):
    category_filter = request.GET.get("category", "")
    articles = BlogArticle.objects.all()
    if category_filter:
        articles = articles.filter(category=category_filter)

    # B2: Paginate articles
    paginator = Paginator(articles, 20)
    page = request.GET.get("page")
    articles_page = paginator.get_page(page)

    active_job = ScanJob.objects.filter(status__in=["pending", "running"], job_type="fiscal").first()

    if request.htmx:
        return render(request, "dashboard/fiscal/_article_list.html", {
            "articles": articles_page,
            "category_filter": category_filter,
        })

    return render(request, "dashboard/fiscal/home.html", {
        "articles": articles_page,
        "category_filter": category_filter,
        "active_job": active_job,
        "active_job_logs": active_job.logs.all() if active_job else [],
        "categories": BlogArticle.CATEGORY_CHOICES,
        "published_count": BlogArticle.objects.filter(status="published").count(),
        "avg_quality": round(BlogArticle.objects.aggregate(avg=db_models.Avg("quality_score"))["avg"] or 0, 1),
    })


def article_detail(request, slug):
    article = get_object_or_404(BlogArticle, slug=slug)
    return render(request, "dashboard/fiscal/article_detail.html", {"article": article})


@ratelimit(key="user_or_ip", rate="3/h", method="POST", block=True)
@require_POST
def start_fiscal_research(request):
    """Start a new fiscal research in a background thread."""
    with transaction.atomic():
        active = ScanJob.objects.select_for_update().filter(
            status__in=["pending", "running"], job_type="fiscal"
        ).first()
        if active:
            return render(request, "dashboard/fiscal/_research_status.html", {"job": active, "logs": active.logs.all()})

        fiscal_team = Team.objects.filter(slug="bedrijfsmonitor").first()
        job = ScanJob.objects.create(
            status="pending",
            job_type="fiscal",
            team=fiscal_team,
            progress_message="Fiscaal onderzoek wordt gestart...",
        )

    _scan_executor.submit(_run_fiscal_background, job.pk)

    return render(request, "dashboard/fiscal/_research_status.html", {"job": job, "logs": []})


@require_POST
def stop_fiscal_research(request, pk):
    """Stop a running fiscal research."""
    job = get_object_or_404(ScanJob, pk=pk, job_type="fiscal")
    if job.status in ("pending", "running"):
        job.status = "failed"
        job.progress_message = "Onderzoek handmatig gestopt"
        job.finished_at = timezone.now()
        job.save()
        ScanLog.objects.create(
            job=job, event_type="error", agent_name="System",
            message="Onderzoek gestopt door gebruiker",
        )
    response = render(request, "dashboard/fiscal/_research_status.html", {"job": job, "logs": job.logs.all()})
    return _toast_response(response, "warning", "Onderzoek gestopt")


def fiscal_research_status(request, pk):
    """HTMX polling endpoint for fiscal research progress."""
    job = get_object_or_404(ScanJob, pk=pk, job_type="fiscal")
    logs = job.logs.all()

    stale = False
    last_activity_seconds = None
    if job.status == "running":
        last_log = logs.order_by("-created_at").first()
        if last_log:
            last_activity_seconds = int((timezone.now() - last_log.created_at).total_seconds())
            if last_activity_seconds > 600:
                stale = True

    return render(request, "dashboard/fiscal/_research_status.html", {
        "job": job,
        "logs": logs,
        "stale": stale,
        "last_activity_seconds": last_activity_seconds,
    })


def htmx_article_list(request):
    category_filter = request.GET.get("category", "")
    articles = BlogArticle.objects.all()
    if category_filter:
        articles = articles.filter(category=category_filter)
    paginator = Paginator(articles, 20)
    articles_page = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/fiscal/_article_list.html", {
        "articles": articles_page,
        "category_filter": category_filter,
    })


# --- Background fiscal research logic ---

def _run_fiscal_background(job_pk: int):
    """Runs the fiscal CrewAI crew in a background thread and saves articles."""
    try:
        import django
        django.setup()
    except Exception:
        logger.error("django.setup() failed in _run_fiscal_background", exc_info=True)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dashboard_scanjob SET status='failed', error_message='Django setup failed' WHERE id=%s",
                    [job_pk],
                )
        except Exception:
            pass
        return

    close_old_connections()
    from dashboard.models import BlogArticle, ScanJob, ScanLog

    job = ScanJob.objects.get(pk=job_pk)
    job.status = "running"
    job.progress_message = "Fiscale agents worden opgestart..."
    job.save(update_fields=["status", "progress_message"])

    def _is_cancelled():
        try:
            return ScanJob.objects.filter(pk=job_pk, status="failed").exists()
        except Exception:
            return False

    def log_callback(event_type, agent_name, message):
        try:
            if _is_cancelled():
                return
            ScanLog.objects.create(
                job_id=job_pk,
                event_type=event_type,
                agent_name=agent_name or "",
                message=message or "",
            )
            if event_type in ("agent", "task_done", "start"):
                short = (message or "")[:295]
                ScanJob.objects.filter(pk=job_pk).update(progress_message=short)
        except Exception:
            logger.error("Error in fiscal log_callback", exc_info=True)

    try:
        log_callback("start", "System", "Fiscaal onderzoek gestart — bronnen worden doorzocht...")

        from fiscal.run import run_fiscal_crew
        results = run_fiscal_crew(log_callback=log_callback)

        # Create BlogArticle objects for each article
        article_count = 0
        for article_data in results["articles"]:
            # Parse deadline_date if present
            deadline_date = None
            raw_deadline = article_data.get("deadline_date")
            if raw_deadline:
                try:
                    from datetime import date as _date
                    deadline_date = _date.fromisoformat(str(raw_deadline)[:10])
                except (ValueError, TypeError):
                    deadline_date = None

            BlogArticle.objects.create(
                title=article_data.get("title", "Zonder titel"),
                intro=article_data.get("intro", ""),
                body=article_data.get("body", ""),
                category=article_data.get("category", "algemeen"),
                sources=article_data.get("sources", []),
                quality_score=article_data.get("quality_score", 5),
                key_takeaways=article_data.get("key_takeaways", []),
                action_items=article_data.get("action_items", []),
                deadline_date=deadline_date,
                relevance_tags=article_data.get("relevance_tags", []),
                scan_job=job,
                total_tokens=results["total_tokens"] // max(len(results["articles"]), 1),
                estimated_cost=results["estimated_cost"] / max(len(results["articles"]), 1),
            )
            article_count += 1

        # Log API usage with job_pk
        try:
            from dashboard.services.api_usage import log_llm_usage
            log_llm_usage(
                service="gemini",
                input_tokens=results.get("total_input", 0),
                output_tokens=results.get("total_output", 0),
                model_name="gemini-3.1-pro-preview",
                job_pk=job_pk,
                description="Fiscaal onderzoek",
            )
        except Exception:
            logger.warning("Could not log fiscal API usage", exc_info=True)

        job.status = "completed"
        job.progress_message = f"Onderzoek afgerond — {article_count} concept-artikelen geschreven"
        job.finished_at = timezone.now()
        job.save()
        log_callback("result", "System", f"Onderzoek afgerond — {article_count} artikelen opgeslagen als concept")

        # Send summary email (failure must not break the job)
        _send_fiscal_summary_email(results["articles"], log_callback)

    except Exception as e:
        logger.error("Fiscal research failed (job=%s)", job_pk, exc_info=True)
        job.status = "failed"
        logger.exception("Job %s failed", job.pk)
        job.error_message = "Er is een fout opgetreden. Controleer de logs voor details."
        job.progress_message = "Onderzoek mislukt"
        job.finished_at = timezone.now()
        job.save()
        log_callback("error", "System", f"Onderzoek mislukt: {type(e).__name__}")
    finally:
        close_old_connections()


# ---------------------------------------------------------------------------
# Sales / CRM
# ---------------------------------------------------------------------------

def sales_home(request):
    groups = _user_groups(request).annotate(
        prospect_count=db_models.Count("prospects"),
    )
    from django.db.models import Count, Q
    counts = Prospect.objects.aggregate(
        total=Count("id"),
        contacted=Count("id", filter=Q(status="contacted")),
        interested=Count("id", filter=Q(status="interested")),
        client=Count("id", filter=Q(status="client")),
    )

    return render(request, "dashboard/sales/home.html", {
        "groups": groups,
        "total_prospects": counts["total"],
        "contacted_count": counts["contacted"],
        "interested_count": counts["interested"],
        "client_count": counts["client"],
    })


def sales_map(request):
    groups = _user_groups(request).annotate(
        prospect_count=Count("prospects"),
    )
    prospects = Prospect.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
    ).prefetch_related("groups")

    prospects_data = []
    for p in prospects:
        prospects_data.append({
            "slug": p.slug,
            "name": p.name,
            "address": p.address,
            "phone": p.phone,
            "email": p.email,
            "website": p.website,
            "status": p.status,
            "status_display": p.get_status_display(),
            "business_type": p.business_type,
            "lat": float(p.latitude),
            "lng": float(p.longitude),
            "groups": [{"slug": g.slug, "name": g.name} for g in p.groups.all()],
        })

    no_coords_count = Prospect.objects.filter(
        Q(latitude__isnull=True) | Q(longitude__isnull=True)
    ).count()

    return render(request, "dashboard/sales/map.html", {
        "groups": groups,
        "prospects_json": prospects_data,
        "total_on_map": len(prospects_data),
        "no_coords_count": no_coords_count,
    })


def sales_search(request):
    groups = _user_groups(request)
    business_types = BusinessType.objects.all()
    return render(request, "dashboard/sales/search.html", {
        "groups": groups,
        "business_types": business_types,
    })


@require_POST
def htmx_sales_search_results(request):
    query = request.POST.get("query", "").strip()
    location = request.POST.get("location", "").strip()
    radius_km = _safe_int(request.POST.get("radius_km"), 10)
    group_slug = request.POST.get("group_slug", "").strip()
    search_mode = request.POST.get("search_mode", "category").strip()

    is_individual = search_mode == "individual"
    default_max = 5 if is_individual else 20
    max_results = _safe_int(request.POST.get("max_results"), default_max)
    max_results = max(1, min(20, max_results))

    min_rating_raw = request.POST.get("min_rating", "").strip()
    min_rating = None
    if min_rating_raw and not is_individual:
        try:
            min_rating = float(min_rating_raw)
        except (ValueError, TypeError):
            pass

    business_type = request.POST.get("business_type", "").strip()
    if is_individual:
        business_type = ""

    if not query:
        return render(request, "dashboard/sales/_search_results.html", {
            "error": "Voer een zoekterm in." if not is_individual else "Voer een bedrijfsnaam in.",
        })

    # Combine query with location for better results (both modes)
    search_query = f"{query} {location}" if location else query

    service = GooglePlacesService()
    api_error = None
    try:
        kwargs = {
            "max_results": max_results,
            "min_rating": min_rating,
        }
        if not is_individual:
            kwargs["radius_m"] = radius_km * 1000
            kwargs["included_type"] = business_type or None

        results = service.text_search(search_query, **kwargs)
    except Exception:
        logger.exception("Google Places search failed")
        results = []
        api_error = "Google Places API is niet beschikbaar. Controleer de API-key en probeer het opnieuw."

    # Log the search
    target_group = None
    if group_slug:
        target_group = _user_groups(request).filter(slug=group_slug).first()

    PlacesSearch.objects.create(
        query=query,
        location=location,
        radius_km=radius_km,
        results_count=len(results),
        target_group=target_group,
    )

    # Mark already-saved prospects (shared dedup logic)
    for r in results:
        match = find_existing_prospect(
            r.get("name", ""),
            address=r.get("address", ""),
            place_id=r.get("place_id", ""),
        )
        r["already_saved"] = match is not None

    unsaved = [r for r in results if not r.get("already_saved")]
    # Encode results as JSON for bulk save (HTML-entity-safe via escapejs in template)
    results_json = json.dumps(results)

    return render(request, "dashboard/sales/_search_results.html", {
        "results": results,
        "searched": True,
        "error": api_error,
        "group_slug": group_slug,
        "unsaved_count": len(unsaved),
        "results_json": results_json,
    })


@require_POST
def htmx_internal_prospect_search(request):
    """Search existing prospects by name, address or email."""
    query = request.POST.get("query", "").strip()
    filter_group = request.POST.get("filter_group", "").strip()
    filter_status = request.POST.get("filter_status", "").strip()

    if not query and not filter_group and not filter_status:
        return render(request, "dashboard/sales/_internal_search_results.html", {
            "error": "Voer een zoekterm in of selecteer een filter.",
        })

    qs = Prospect.objects.prefetch_related("groups").select_related("assigned_template")
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | Q(address__icontains=query) | Q(email__icontains=query)
        )
    if filter_group:
        qs = qs.filter(groups__slug=filter_group)
    if filter_status:
        qs = qs.filter(status=filter_status)

    prospects = qs.distinct().order_by("name")[:50]

    return render(request, "dashboard/sales/_internal_search_results.html", {
        "prospects": prospects,
        "all_groups": _user_groups(request),
        "searched": True,
        "result_count": len(prospects),
    })


@require_POST
def htmx_prospect_save(request):
    """Save a single prospect from search results."""
    place_id = request.POST.get("place_id", "").strip()
    name = request.POST.get("name", "").strip()
    group_slug = request.POST.get("group_slug", "").strip()

    if not name:
        return render(request, "dashboard/sales/_search_results.html", {
            "error": "Naam is verplicht.",
        })

    # Get or create prospect (shared dedup logic)
    address = request.POST.get("address", "").strip()
    prospect = find_existing_prospect(name, address=address, place_id=place_id)

    if not prospect:
        website = request.POST.get("website", "").strip()
        if website and not website.startswith(("http://", "https://")):
            website = "https://" + website
        prospect = Prospect(
            place_id=place_id,
            name=name,
            address=address,
            phone=request.POST.get("phone", ""),
            website=website,
            business_type=request.POST.get("business_type", ""),
        )
        rating = request.POST.get("rating", "")
        if rating:
            try:
                prospect.google_rating = float(rating)
            except (ValueError, TypeError):
                pass
        reviews = request.POST.get("reviews_count", "0")
        prospect.google_reviews_count = _safe_int(reviews, 0)
        lat = request.POST.get("latitude", "")
        lng = request.POST.get("longitude", "")
        if lat:
            try:
                prospect.latitude = float(lat)
            except (ValueError, TypeError):
                pass
        if lng:
            try:
                prospect.longitude = float(lng)
            except (ValueError, TypeError):
                pass
        prospect.save()

        # Auto-scrape contact info from website
        if prospect.website and not prospect.email:
            try:
                info = scrape_contact_info(prospect.website)
                update_fields = []
                if info.email:
                    prospect.email = info.email
                    update_fields.append("email")
                if info.contact_first_name and not prospect.contact_first_name:
                    prospect.contact_first_name = info.contact_first_name
                    update_fields.append("contact_first_name")
                if info.contact_last_name and not prospect.contact_last_name:
                    prospect.contact_last_name = info.contact_last_name
                    update_fields.append("contact_last_name")
                if not prospect.aanhef:
                    prospect.aanhef = "Geachte heer/mevrouw"
                    update_fields.append("aanhef")
                if update_fields:
                    prospect.save(update_fields=update_fields)
            except Exception:
                logger.exception("Contact scrape failed for %s", prospect.website)

    # Add to group if specified
    if group_slug:
        group = _user_groups(request).filter(slug=group_slug).first()
        if group:
            prospect.groups.add(group)

    # Return a "saved" badge to replace the button
    extra_info = ""
    if prospect.email:
        extra_info += (
            f' <span class="text-gray-400">·</span> '
            f'<span class="text-indigo-600">{html_escape(prospect.email)}</span>'
        )
    if prospect.contact_first_name or prospect.contact_last_name:
        name = f"{prospect.contact_first_name} {prospect.contact_last_name}".strip()
        extra_info += (
            f' <span class="text-gray-400">·</span> '
            f'<span class="text-gray-600">{html_escape(name)}</span>'
        )
    return HttpResponse(
        f'<span class="inline-flex items-center gap-1 text-xs font-medium text-emerald-600">'
        f'<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
        f'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>'
        f'</svg>Opgeslagen{extra_info}</span>'
    )


@require_POST
def htmx_prospect_save_all(request):
    """Bulk-save all search results into a group."""
    group_slug = request.POST.get("group_slug", "").strip()
    results_raw = request.POST.get("results_json", "")

    try:
        results = json.loads(results_raw)
    except (json.JSONDecodeError, TypeError):
        logger.warning("htmx_prospect_save_all: JSON parse failed for results_json")
        return _toast_response(
            HttpResponse(""),
            "error",
            "Ongeldige data ontvangen.",
        )

    if not isinstance(results, list):
        logger.warning("htmx_prospect_save_all: results_json is not a list")
        return _toast_response(
            HttpResponse(""),
            "error",
            "Ongeldige data ontvangen.",
        )

    group = _user_groups(request).filter(slug=group_slug).first() if group_slug else None
    saved_count = 0

    for r in results:
        if r.get("already_saved"):
            continue

        name = (r.get("name") or "").strip()
        if not name:
            continue

        place_id = (r.get("place_id") or "").strip()
        address = (r.get("address") or "").strip()

        # Get or create (shared dedup logic)
        prospect = find_existing_prospect(name, address=address, place_id=place_id)

        if not prospect:
            prospect = Prospect(
                place_id=place_id,
                name=name,
                address=address,
                phone=r.get("phone") or "",
                website=r.get("website") or "",
                business_type=r.get("business_type") or "",
            )
            rating = r.get("rating")
            if rating:
                try:
                    prospect.google_rating = float(rating)
                except (ValueError, TypeError):
                    pass
            prospect.google_reviews_count = _safe_int(r.get("reviews_count"), 0)
            lat = r.get("latitude")
            if lat:
                try:
                    prospect.latitude = float(lat)
                except (ValueError, TypeError):
                    pass
            lng = r.get("longitude")
            if lng:
                try:
                    prospect.longitude = float(lng)
                except (ValueError, TypeError):
                    pass
            prospect.save()

            # Auto-scrape contact info from website
            if prospect.website and not prospect.email:
                try:
                    info = scrape_contact_info(prospect.website)
                    update_fields = []
                    if info.email:
                        prospect.email = info.email
                        update_fields.append("email")
                    if info.contact_first_name and not prospect.contact_first_name:
                        prospect.contact_first_name = info.contact_first_name
                        update_fields.append("contact_first_name")
                    if info.contact_last_name and not prospect.contact_last_name:
                        prospect.contact_last_name = info.contact_last_name
                        update_fields.append("contact_last_name")
                    if not prospect.aanhef:
                        prospect.aanhef = "Geachte heer/mevrouw"
                        update_fields.append("aanhef")
                    if update_fields:
                        prospect.save(update_fields=update_fields)
                except Exception:
                    logger.exception("Contact scrape failed for %s", prospect.website)

        if group:
            prospect.groups.add(group)
        saved_count += 1

    # Re-render results with all marked as saved
    for r in results:
        r["already_saved"] = True

    response = render(request, "dashboard/sales/_search_results.html", {
        "results": results,
        "searched": True,
        "group_slug": group_slug,
        "unsaved_count": 0,
        "results_json": json.dumps(results),
    })
    return _toast_response(response, "success", f"{saved_count} prospects opgeslagen")


@require_POST
def htmx_prospect_check_duplicate(request):
    """Live duplicate check while typing prospect name."""
    name = request.POST.get("name", "").strip()
    group_slug = request.POST.get("group_slug", "").strip()
    if len(name) < 3:
        return HttpResponse("")

    matches = list(Prospect.objects.filter(name__icontains=name)[:5])
    group = _user_groups(request).filter(slug=group_slug).first() if group_slug else None
    group_prospect_ids = set()
    if group:
        group_prospect_ids = set(group.prospects.values_list("pk", flat=True))

    for m in matches:
        m.in_current_group = m.pk in group_prospect_ids

    return render(request, "dashboard/sales/_prospect_duplicate_check.html", {
        "matches": matches,
        "group": group,
    })


@require_POST
def htmx_prospect_manual_add(request):
    """Manually add a prospect and attach to group."""
    name = request.POST.get("name", "").strip()
    group_slug = request.POST.get("group_slug", "").strip()
    if not name:
        resp = HttpResponse("")
        return _toast_response(resp, "error", "Naam is verplicht.")

    group = _user_groups(request).filter(slug=group_slug).first() if group_slug else None

    # Check for existing prospect (shared dedup logic)
    address = request.POST.get("address", "").strip()
    logger.info("Manual add POST data: status=%s, contact_channel=%s, assigned_template=%s, linkedin_url=%s",
                request.POST.get("status"), request.POST.get("contact_channel"),
                request.POST.get("assigned_template"), request.POST.get("linkedin_url"))
    prospect = find_existing_prospect(name, address=address)
    if not prospect:
        website = request.POST.get("website", "").strip()
        if website and not website.startswith(("http://", "https://")):
            website = "https://" + website
        linkedin_url = request.POST.get("linkedin_url", "").strip()
        if linkedin_url and not linkedin_url.startswith(("http://", "https://")):
            linkedin_url = "https://" + linkedin_url
        status = request.POST.get("status", "new").strip()
        if status not in {c[0] for c in Prospect.STATUS_CHOICES}:
            status = "new"
        contact_channel = request.POST.get("contact_channel", "").strip()
        if contact_channel and contact_channel not in {c[0] for c in Prospect.CHANNEL_CHOICES}:
            contact_channel = ""
        prospect = Prospect(
            name=name,
            address=address,
            phone=request.POST.get("phone", "").strip(),
            website=website,
            linkedin_url=linkedin_url,
            status=status,
            contact_channel=contact_channel,
            notes=request.POST.get("notes", "").strip(),
            contact_first_name=request.POST.get("contact_first_name", "").strip(),
            contact_last_name=request.POST.get("contact_last_name", "").strip(),
            email=request.POST.get("email", "").strip(),
            aanhef=request.POST.get("aanhef", "").strip(),
        )
        template_id = request.POST.get("assigned_template", "").strip()
        if template_id:
            prospect.assigned_template = ResponseTemplate.objects.filter(pk=template_id).first()
        prospect.save()
        from dashboard.services.geocoding import geocode_prospect
        geocode_prospect(prospect)

    if group:
        prospect.groups.add(group)

    # Annotate and prefetch for template
    prospect = Prospect.objects.filter(pk=prospect.pk).select_related("assigned_template").prefetch_related("responses__template").annotate(
        has_responses=Exists(ProspectResponse.objects.filter(prospect=OuterRef("pk")))
    ).first()

    resp = render(request, "dashboard/sales/_prospect_row.html", {
        "prospect": prospect,
    })
    return _toast_response(resp, "success", f"Prospect '{prospect.name}' toegevoegd")


@require_POST
def htmx_geocode_prospects(request):
    """Geocode prospects without coordinates (max 50 at a time)."""
    from dashboard.services.geocoding import geocode_prospect

    prospects = list(
        Prospect.objects.filter(
            Q(latitude__isnull=True) | Q(longitude__isnull=True)
        ).exclude(address="")[:50]
    )

    geocoded = 0
    for p in prospects:
        if geocode_prospect(p):
            geocoded += 1

    resp = HttpResponse("")
    resp["HX-Refresh"] = "true"
    return _toast_response(
        resp, "success",
        f"{geocoded} van {len(prospects)} prospects geocoded."
    )


@require_POST
def htmx_prospect_link_to_group(request):
    """Link an existing prospect to a group."""
    prospect_id = request.POST.get("prospect_id", "")
    group_slug = request.POST.get("group_slug", "").strip()

    prospect = get_object_or_404(Prospect, pk=prospect_id)
    group = get_object_or_404(ProspectGroup, slug=group_slug)
    prospect.groups.add(group)

    # Annotate and prefetch for template
    prospect = Prospect.objects.filter(pk=prospect.pk).select_related("assigned_template").prefetch_related("responses__template").annotate(
        has_responses=Exists(ProspectResponse.objects.filter(prospect=OuterRef("pk")))
    ).first()

    resp = render(request, "dashboard/sales/_prospect_row.html", {
        "prospect": prospect,
        "oob_swap": True,
    })
    return _toast_response(resp, "success", f"Prospect '{prospect.name}' gekoppeld aan groep")


def prospect_group_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if name:
            group = ProspectGroup(name=name, description=description, owner=request.user)
            group.save()
            return redirect("dashboard:prospect_group_detail", slug=group.slug)
    return render(request, "dashboard/sales/_group_form.html", {"group": None})


def prospect_group_detail(request, slug):
    group = _get_user_group(request, slug)
    prospects = group.prospects.select_related("assigned_template").prefetch_related("responses__template").annotate(
        has_responses=Exists(ProspectResponse.objects.filter(prospect=OuterRef("pk"))),
        last_sent_at=Max("responses__sent_at"),
    )

    status_filter = request.GET.get("status", "")
    if status_filter:
        prospects = prospects.filter(status=status_filter)

    return render(request, "dashboard/sales/group_detail.html", {
        "group": group,
        "prospects": prospects,
        "response_templates": ResponseTemplate.objects.select_related("category").all(),
    })


def prospect_group_edit(request, slug):
    group = _get_user_group(request, slug)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if name:
            name_changed = name != group.name
            group.name = name
            group.description = description
            if name_changed:
                from django.utils.text import slugify
                group.slug = slugify(name)[:190]
                _save_with_unique_slug(group, slug_field_max=190, slug_source_attr="name")
            else:
                group.save()
            return redirect("dashboard:prospect_group_detail", slug=group.slug)
    return render(request, "dashboard/sales/_group_form.html", {"group": group})


@require_POST
def prospect_group_delete(request, slug):
    group = _get_user_group(request, slug)
    with transaction.atomic():
        group.delete()
    messages.success(request, "Groep verwijderd")
    return redirect("dashboard:sales_home")


def htmx_prospect_popup(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)
    responses = list(prospect.responses.select_related("template").all())
    response_templates = ResponseTemplate.objects.all()

    # Fetch tracking events from local DB (single aggregated query)
    tokens = [r.tracking_token for r in responses]
    stats = (
        TrackingEvent.objects.filter(token__in=tokens)
        .values("token")
        .annotate(
            open_count=Count("pk", filter=Q(event_type="open")),
            click_count=Count("pk", filter=Q(event_type="click")),
        )
    )
    stats_map = {s["token"]: s for s in stats}
    for resp in responses:
        s = stats_map.get(resp.tracking_token, {})
        resp.open_count = s.get("open_count", 0)
        resp.click_count = s.get("click_count", 0)
        resp.is_stale = (
            resp.open_count == 0
            and resp.sent_at
            and (timezone.now() - resp.sent_at).days >= 7
        )

    return render(request, "dashboard/sales/_prospect_popup.html", {
        "prospect": prospect,
        "status_choices": Prospect.STATUS_CHOICES,
        "channel_choices": Prospect.CHANNEL_CHOICES,
        "aanhef_choices": Prospect.AANHEF_CHOICES,
        "responses": responses,
        "response_templates": response_templates,
    })


@require_POST
def htmx_prospect_status(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)
    new_status = request.POST.get("status", prospect.status)
    new_channel = request.POST.get("contact_channel", prospect.contact_channel)
    new_notes = request.POST.get("notes", prospect.notes)
    new_linkedin = request.POST.get("linkedin_url", prospect.linkedin_url)
    new_first = request.POST.get("contact_first_name", prospect.contact_first_name)
    new_last = request.POST.get("contact_last_name", prospect.contact_last_name)
    new_email = request.POST.get("email", prospect.email)
    new_aanhef = request.POST.get("aanhef", prospect.aanhef)
    new_template_id = request.POST.get("assigned_template_id", "").strip()

    # Validate choice fields
    valid_statuses = {c[0] for c in Prospect.STATUS_CHOICES}
    if new_status not in valid_statuses:
        new_status = prospect.status

    # Auto-set contacted_at on first contact
    if new_status != "new" and prospect.status == "new" and not prospect.contacted_at:
        prospect.contacted_at = timezone.now()

    prospect.status = new_status
    prospect.contact_channel = new_channel
    prospect.notes = new_notes
    prospect.linkedin_url = new_linkedin
    prospect.contact_first_name = new_first
    prospect.contact_last_name = new_last
    prospect.email = new_email
    prospect.aanhef = new_aanhef
    prospect.assigned_template_id = _safe_int(new_template_id, 0) or None
    prospect.save()

    # Re-fetch with prefetch for response template display
    prospect = Prospect.objects.filter(pk=prospect.pk).select_related("assigned_template").prefetch_related("responses__template").first()

    # Return OOB swap: empty modal + updated row
    row_html = render(request, "dashboard/sales/_prospect_row.html", {"prospect": prospect}).content.decode()
    oob_row = row_html.replace(
        f'id="prospect-row-{prospect.slug}"',
        f'id="prospect-row-{prospect.slug}" hx-swap-oob="outerHTML:#prospect-row-{prospect.slug}"',
    )
    response_html = f"<div></div>{oob_row}"
    return _toast_response(HttpResponse(response_html), "success", "Prospect bijgewerkt")


@require_POST
def htmx_prospect_delete(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)
    row_id = f"prospect-row-{prospect.slug}"
    prospect.delete()
    # Empty primary content (clears modal) + OOB delete (removes table row)
    oob_html = f'<tr id="{row_id}" hx-swap-oob="delete:#{row_id}"></tr>'
    response = HttpResponse(f"<div></div>{oob_html}")
    return _toast_response(response, "success", "Prospect verwijderd")


@require_POST
def htmx_prospect_bulk_update(request):
    """Bulk update status/channel for multiple prospects."""
    slugs = request.POST.getlist("slugs")
    new_status = request.POST.get("status", "").strip()
    new_channel = request.POST.get("contact_channel", "").strip()
    new_aanhef = request.POST.get("aanhef", "").strip()
    template_id = request.POST.get("template_id", "").strip()
    group_slug = request.POST.get("group_slug", "").strip()

    if not slugs:
        return _toast_response(HttpResponse(""), "error", "Geen prospects geselecteerd.")

    template = None
    if template_id:
        template = ResponseTemplate.objects.filter(pk=template_id).first()

    # Validate choice fields
    valid_statuses = {c[0] for c in Prospect.STATUS_CHOICES}
    if new_status and new_status not in valid_statuses:
        new_status = ""

    group = get_object_or_404(ProspectGroup, slug=group_slug)
    prospects = group.prospects.filter(slug__in=slugs)
    updated = 0

    with transaction.atomic():
        for prospect in prospects:
            changed = False
            if new_status and new_status != prospect.status:
                # Auto-set contacted_at on first contact
                if new_status != "new" and prospect.status == "new" and not prospect.contacted_at:
                    prospect.contacted_at = timezone.now()
                prospect.status = new_status
                changed = True
            if new_channel and new_channel != prospect.contact_channel:
                prospect.contact_channel = new_channel
                changed = True
            if new_aanhef and new_aanhef != prospect.aanhef:
                prospect.aanhef = new_aanhef
                changed = True
            if template and prospect.assigned_template_id != template.pk:
                prospect.assigned_template = template
                changed = True
            if changed:
                prospect.save()
                updated += 1

    # Re-render all prospects for this group
    all_prospects = group.prospects.select_related("assigned_template").prefetch_related("responses__template").all()
    rows_html = ""
    for p in all_prospects:
        rows_html += render(request, "dashboard/sales/_prospect_row.html", {"prospect": p}).content.decode()

    return _toast_response(HttpResponse(rows_html), "success", f"{updated} prospects bijgewerkt")


@require_POST
def htmx_prospect_bulk_delete(request):
    """Bulk delete multiple prospects from a group."""
    slugs = request.POST.getlist("slugs")
    group_slug = request.POST.get("group_slug", "").strip()

    if not slugs:
        return _toast_response(HttpResponse(""), "error", "Geen prospects geselecteerd.")

    group = _get_user_group(request, group_slug)
    deleted_count = group.prospects.filter(slug__in=slugs).delete()[0]

    # Check if group still has prospects
    remaining = group.prospects.select_related("assigned_template").prefetch_related("responses__template").all()
    if not remaining.exists():
        response = HttpResponse("")
        response["HX-Redirect"] = "/sales/"
        return response

    rows_html = ""
    for p in remaining:
        rows_html += render(request, "dashboard/sales/_prospect_row.html", {"prospect": p}).content.decode()

    return _toast_response(HttpResponse(rows_html), "success", f"{deleted_count} prospects verwijderd")


# ===================================================================
# Bulk Email views
# ===================================================================

@require_POST
def bulk_email_preview(request):
    """Preview page for bulk email sending."""
    slugs = request.POST.getlist("slugs")
    template_id = request.POST.get("template_id", "").strip()
    group_slug = request.POST.get("group_slug", "")

    if not slugs or not group_slug:
        messages.error(request, "Ongeldige selectie.")
        return redirect("dashboard:sales_home")

    group = get_object_or_404(ProspectGroup, slug=group_slug)
    template = ResponseTemplate.objects.filter(pk=template_id).first() if template_id else None
    prospects = Prospect.objects.filter(slug__in=slugs).select_related("assigned_template")

    # Check email settings
    from accounts.models import EmailSettings
    email_settings = EmailSettings.objects.filter(user=request.user).first()
    email_configured = email_settings and email_settings.is_configured

    previews = []
    with_email = 0
    skipped = 0
    dedup_cutoff = timezone.now() - timedelta(hours=24)
    for p in prospects:
        tpl = template or p.assigned_template
        if not tpl:
            skipped += 1
            continue
        has_email = bool(p.email)
        if has_email:
            with_email += 1
        subject, body, html_body = tpl.interpolate(p)
        text_preview = ResponseTemplate.strip_html_to_text(html_body) if html_body else body
        recently_sent = ProspectResponse.objects.filter(
            prospect=p, template=tpl, sent_at__gte=dedup_cutoff
        ).exists() if has_email else False
        previews.append({
            "prospect": p,
            "has_email": has_email,
            "subject": subject,
            "body": body,
            "text_preview": text_preview,
            "html_body": html_body,
            "has_html": bool(html_body),
            "aanhef": p.aanhef,
            "template": tpl,
            "recently_sent": recently_sent,
        })

    if not previews:
        messages.error(request, "Geen prospects met een template gevonden. Wijs eerst een template toe via 'Toepassen'.")
        return redirect("dashboard:prospect_group_detail", slug=group_slug)

    # --- Link validation: check external URLs in templates (max 10, with timeout) ---
    import re as _re
    import requests as _requests
    _MAX_LINK_CHECKS = 10
    seen_urls: set[str] = set()
    for item in previews:
        content = item.get("html_body") or item.get("body") or ""
        for url in _re.findall(r'https?://(?:www\.)?fenofin\.nl[^\s"<>\'&]*', content):
            seen_urls.add(url)
    link_results = []
    has_broken_links = False
    for url in sorted(seen_urls)[:_MAX_LINK_CHECKS]:
        try:
            resp = _requests.head(url, timeout=3, allow_redirects=True)
            ok = resp.status_code == 200
        except Exception:
            ok = False
            resp = None
        if not ok:
            has_broken_links = True
        link_results.append({
            "url": url,
            "status": resp.status_code if resp else 0,
            "ok": ok,
        })
    if len(seen_urls) > _MAX_LINK_CHECKS:
        link_results.append({
            "url": f"... en {len(seen_urls) - _MAX_LINK_CHECKS} meer (niet gecontroleerd)",
            "status": 0,
            "ok": True,
        })

    return render(request, "dashboard/sales/bulk_email_preview.html", {
        "group": group,
        "template": template,
        "previews": previews,
        "total_count": len(previews),
        "with_email_count": with_email,
        "without_email_count": len(previews) - with_email,
        "skipped_count": skipped,
        "email_configured": email_configured,
        "from_address": email_settings.from_header if email_configured else "",
        "aanhef_choices": Prospect.AANHEF_CHOICES,
        "link_results": link_results,
        "has_broken_links": has_broken_links,
    })


@xframe_options_sameorigin
def bulk_email_prospect_preview(request, slug):
    """Render interpolated HTML email for a single prospect (shown in iframe)."""
    template_id = request.GET.get("template_id", "").strip()
    prospect = get_object_or_404(Prospect.objects.select_related("assigned_template"), slug=slug)
    if template_id:
        template = get_object_or_404(ResponseTemplate, pk=template_id)
    elif prospect.assigned_template:
        template = prospect.assigned_template
    else:
        return HttpResponse("<p>Geen template toegewezen.</p>")
    _, body, html_body = template.interpolate(prospect)
    if html_body:
        return HttpResponse(html_body)
    plain_html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<style>body{font-family:Arial,sans-serif;max-width:600px;margin:40px auto;padding:20px;color:#333;line-height:1.7;}</style>"
        "</head><body>"
        f"<div style='white-space:pre-line'>{html_escape(body)}</div>"
        "</body></html>"
    )
    return HttpResponse(plain_html)


@require_POST
def htmx_send_test_email(request):
    """Send a test email to the logged-in user's own address."""
    template_id = request.POST.get("template_id", "")
    prospect_slug = request.POST.get("prospect_slug", "")

    if not template_id or not prospect_slug:
        return _toast_response(HttpResponse(""), "error", "Ongeldige selectie.")

    from accounts.models import EmailSettings
    try:
        email_settings = EmailSettings.objects.get(user=request.user)
    except EmailSettings.DoesNotExist:
        return _toast_response(HttpResponse(""), "error", "E-mail instellingen ontbreken.")

    if not email_settings.is_configured:
        return _toast_response(HttpResponse(""), "error", "E-mail instellingen niet geconfigureerd.")

    prospect = get_object_or_404(Prospect, slug=prospect_slug)
    template = get_object_or_404(ResponseTemplate, pk=template_id)
    subject, body, html_tpl = template.interpolate(prospect)

    if html_tpl:
        html_body = html_tpl
    else:
        html_body = f"<html><body><div style='white-space:pre-line; font-family:sans-serif'>{html_escape(body)}</div></body></html>"

    from accounts.services.email_backend import send_email_from_settings
    try:
        send_email_from_settings(email_settings, email_settings.smtp_user, f"[TEST] {subject}", body, html_body)
    except Exception as exc:
        logger.exception("Test email failed")
        return _toast_response(HttpResponse(""), "error", "Verzenden mislukt. Controleer de e-mailinstellingen.")

    return _toast_response(HttpResponse(""), "success", f"Test e-mail verzonden naar {email_settings.smtp_user}")


@require_POST
@ratelimit(key="user_or_ip", rate="5/h", method="POST", block=True)
def htmx_bulk_email_send(request):
    """Send bulk emails in background thread."""
    slugs = request.POST.getlist("slugs")
    template_id = request.POST.get("template_id", "").strip()
    group_slug = request.POST.get("group_slug", "")

    if not slugs:
        return _toast_response(HttpResponse(""), "error", "Ongeldige selectie.")

    from accounts.models import EmailSettings
    try:
        email_settings = EmailSettings.objects.get(user=request.user)
    except EmailSettings.DoesNotExist:
        return _toast_response(HttpResponse(""), "error", "E-mail instellingen ontbreken.")

    if not email_settings.is_configured:
        return _toast_response(HttpResponse(""), "error", "E-mail instellingen incompleet.")

    template = ResponseTemplate.objects.filter(pk=template_id).first() if template_id else None
    # Only allow sending to prospects in groups owned by the current user
    user_group_pks = _user_groups(request).values_list("pk", flat=True)
    prospects = Prospect.objects.filter(
        slug__in=slugs, groups__pk__in=user_group_pks,
    ).exclude(email="").select_related("assigned_template").distinct()
    prospect_pks = list(prospects.values_list("pk", flat=True))

    if not prospect_pks:
        return _toast_response(HttpResponse(""), "error", "Geen prospects met e-mailadres gevonden.")

    # Submit to background thread
    _scan_executor.submit(_send_bulk_emails, prospect_pks, template.pk if template else None, email_settings.pk)

    response = HttpResponse("")
    response["HX-Redirect"] = f"/sales/groepen/{group_slug}/" if group_slug else "/sales/"
    return _toast_response(response, "success", f"{len(prospect_pks)} e-mails worden verzonden...")


def _send_bulk_emails(prospect_pks, template_pk, email_settings_pk):
    """Background worker: send emails via Microsoft Graph API."""
    import time

    from accounts.models import EmailSettings
    from accounts.services.email_backend import send_email_from_settings

    try:
        es = EmailSettings.objects.get(pk=email_settings_pk)
        global_template = ResponseTemplate.objects.filter(pk=template_pk).first() if template_pk else None
        prospects = Prospect.objects.filter(pk__in=prospect_pks).select_related("assigned_template")

        for prospect in prospects:
            try:
                template = global_template or prospect.assigned_template
                if not template:
                    logger.warning("Skipping %s: no template", prospect.name)
                    continue
                subject, body, html_tpl = template.interpolate(prospect)
                if html_tpl:
                    html_body = html_tpl
                else:
                    html_body = f"<html><body><div style='white-space:pre-line; font-family:sans-serif'>{html_escape(body)}</div></body></html>"

                # Dedup warning (no longer blocks — user decides in preview)
                cutoff = timezone.now() - timedelta(hours=24)
                if ProspectResponse.objects.filter(
                    prospect=prospect, template=template, sent_at__gte=cutoff
                ).exists():
                    logger.warning("Opnieuw verzenden naar %s (al gemaild in afgelopen 24u)", prospect.name)

                pr = ProspectResponse.objects.create(
                    prospect=prospect,
                    template=template,
                    sent_at=None,
                    notes="Bezig met verzenden...",
                )

                send_email_from_settings(es, prospect.email, subject, body, html_body)

                pr.sent_at = timezone.now()
                pr.notes = "Verzonden per e-mail"
                pr.save()

                with transaction.atomic():
                    p = Prospect.objects.select_for_update().get(pk=prospect.pk)
                    if p.status in ("new", "not_contacted"):
                        p.status = "contacted"
                        p.contact_channel = "email"
                        if not p.contacted_at:
                            p.contacted_at = timezone.now()
                        p.save(update_fields=["status", "contact_channel", "contacted_at"])

                time.sleep(0.3)

            except Exception as e:
                logger.warning("Fout bij verzenden naar %s: %s", prospect.email, e)
                if 'pr' in locals():
                    pr.notes = f"Fout bij verzenden: {e}"
                    pr.save()

    except Exception as e:
        logger.error("Bulk email fout: %s", e)


# ===================================================================
# Sales Diary views
# ===================================================================

def sales_diary(request):
    entries = SalesDiary.objects.all()
    paginator = Paginator(entries, 20)
    page = paginator.get_page(request.GET.get("page"))
    today = timezone.now().date()
    today_entry = SalesDiary.objects.filter(date=today).first()
    return render(request, "dashboard/sales/diary.html", {
        "page_obj": page,
        "today": today,
        "today_entry": today_entry,
    })


def sales_diary_edit(request, date):
    from datetime import date as date_type
    try:
        parsed_date = date_type.fromisoformat(date)
    except ValueError:
        raise Http404("Ongeldige datum")

    entry, _created = SalesDiary.objects.get_or_create(date=parsed_date)

    if request.method == "POST":
        entry.results = request.POST.get("results", "").strip()
        entry.notes = request.POST.get("notes", "").strip()
        entry.save()

        # Process goal rows
        goal_ids = request.POST.getlist("goal_id")
        goal_descs = request.POST.getlist("goal_desc")
        goal_targets = request.POST.getlist("goal_target")
        goal_actuals = request.POST.getlist("goal_actual")

        submitted_ids = set()
        for i in range(len(goal_descs)):
            gid = _safe_int(goal_ids[i], 0) if i < len(goal_ids) else 0
            desc = goal_descs[i].strip()
            target = max(0, _safe_int(goal_targets[i] if i < len(goal_targets) else 0, 0))
            actual = max(0, _safe_int(goal_actuals[i] if i < len(goal_actuals) else 0, 0))

            if gid:
                entry.diary_goals.filter(id=gid).update(
                    description=desc, prospects_target=target,
                    prospects_contacted_actual=actual, order=i)
                submitted_ids.add(gid)
            else:
                if not desc:
                    continue
                new_goal = entry.diary_goals.create(
                    description=desc, prospects_target=target,
                    prospects_contacted_actual=actual, order=i)
                submitted_ids.add(new_goal.id)

        entry.diary_goals.exclude(id__in=submitted_ids).delete()
        messages.success(request, "Dagboek opgeslagen.")
        return redirect("dashboard:sales_diary")

    goals = entry.diary_goals.all()
    return render(request, "dashboard/sales/diary_edit.html", {"entry": entry, "goals": goals})


@require_POST
def htmx_sales_diary_delete(request, date):
    from datetime import date as date_type
    try:
        parsed_date = date_type.fromisoformat(date)
    except ValueError:
        raise Http404("Ongeldige datum")

    SalesDiary.objects.filter(date=parsed_date).delete()
    messages.success(request, "Dagboek entry verwijderd")
    return redirect("dashboard:sales_diary")


# ---------------------------------------------------------------------------
# Response Templates
# ---------------------------------------------------------------------------

def sales_templates(request):
    templates = ResponseTemplate.objects.select_related("category").order_by("order", "name")
    categories = TemplateCategory.objects.all()
    return render(request, "dashboard/sales/templates_list.html", {
        "templates": templates,
        "categories": categories,
        "color_choices": TemplateCategory.COLOR_CHOICES,
    })


def response_template_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category_id = request.POST.get("category", "")
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        html_template = request.POST.get("html_template", "").strip()
        if name and body:
            category = TemplateCategory.objects.filter(pk=category_id).first() if category_id else None
            tpl = ResponseTemplate(name=name, category=category, subject=subject, body=body, html_template=html_template)
            tpl.save()
            return redirect("dashboard:sales_templates")
    return render(request, "dashboard/sales/template_edit.html", {
        "template": None,
        "categories": TemplateCategory.objects.all(),
    })


def response_template_edit(request, slug):
    tpl = get_object_or_404(ResponseTemplate, slug=slug)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category_id = request.POST.get("category", "")
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()
        html_template = request.POST.get("html_template", "").strip()
        if name and body:
            tpl.name = name
            tpl.category = TemplateCategory.objects.filter(pk=category_id).first() if category_id else None
            tpl.subject = subject
            tpl.body = body
            tpl.html_template = html_template
            tpl.save()
            return redirect("dashboard:sales_templates")
    return render(request, "dashboard/sales/template_edit.html", {
        "template": tpl,
        "categories": TemplateCategory.objects.all(),
    })


@xframe_options_sameorigin
def response_template_preview(request, slug):
    """Render a template with dummy data for preview."""
    tpl = get_object_or_404(ResponseTemplate, slug=slug)

    class _DummyProspect:
        aanhef = "Geachte heer"
        contact_first_name = "Jan"
        contact_last_name = "de Vries"
        name = "Voorbeeld Administratiekantoor B.V."
        email = "info@voorbeeld.nl"

    _, body, html_body = tpl.interpolate(_DummyProspect())
    if html_body:
        return HttpResponse(html_body)
    # Fallback: render plain text in a simple styled wrapper
    plain_html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<style>body{font-family:Arial,sans-serif;max-width:600px;margin:40px auto;padding:20px;color:#333;line-height:1.7;}</style>"
        "</head><body>"
        f"<div style='white-space:pre-line'>{html_escape(body)}</div>"
        "</body></html>"
    )
    return HttpResponse(plain_html)


@require_POST
def response_template_delete(request, slug):
    tpl = get_object_or_404(ResponseTemplate, slug=slug)
    tpl.delete()
    messages.success(request, "Template verwijderd")
    return redirect("dashboard:sales_templates")


@require_POST
def response_template_toggle_star(request, slug):
    tpl = get_object_or_404(ResponseTemplate, slug=slug)
    tpl.is_starred = not tpl.is_starred
    tpl.save(update_fields=["is_starred"])
    response = render(request, "dashboard/sales/_star_button.html", {"tpl": tpl})
    response["HX-Trigger"] = json.dumps({"starToggled": {"pk": tpl.pk, "starred": tpl.is_starred}})
    return response


@require_POST
def response_template_reorder(request):
    try:
        data = json.loads(request.body)
        order_list = data.get("order", [])
        with transaction.atomic():
            for i, pk in enumerate(order_list):
                ResponseTemplate.objects.filter(pk=int(pk)).update(order=i)
        return JsonResponse({"ok": True})
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid data"}, status=400)


@require_POST
def response_template_move(request, pk, direction):
    """Move a template up or down in the order."""
    template = get_object_or_404(ResponseTemplate, pk=pk)
    templates = list(ResponseTemplate.objects.order_by("order", "name").values_list("pk", flat=True))
    idx = templates.index(template.pk)

    if direction == "up" and idx > 0:
        swap_idx = idx - 1
    elif direction == "down" and idx < len(templates) - 1:
        swap_idx = idx + 1
    else:
        return redirect("dashboard:sales_templates")

    # Swap positions in list, then save all indices as order values
    templates[idx], templates[swap_idx] = templates[swap_idx], templates[idx]
    with transaction.atomic():
        for i, tpl_pk in enumerate(templates):
            ResponseTemplate.objects.filter(pk=tpl_pk).update(order=i)

    messages.success(request, "Volgorde aangepast")
    return redirect("dashboard:sales_templates")


# ---------------------------------------------------------------------------
# Template Category CRUD (HTMX)
# ---------------------------------------------------------------------------

def _render_categories_partial(request):
    response = HttpResponse(status=204)
    response["HX-Redirect"] = reverse("dashboard:sales_templates")
    return response


@require_POST
def template_category_add(request):
    name = request.POST.get("name", "").strip()
    color = request.POST.get("color", "indigo")
    if name:
        TemplateCategory.objects.create(name=name, color=color)
    return _render_categories_partial(request)


@require_POST
def template_category_edit(request, pk):
    cat = get_object_or_404(TemplateCategory, pk=pk)
    cat.name = request.POST.get("name", cat.name).strip() or cat.name
    cat.color = request.POST.get("color", cat.color)
    cat.save()
    return _render_categories_partial(request)


@require_POST
def template_category_delete(request, pk):
    TemplateCategory.objects.filter(pk=pk).delete()
    return _render_categories_partial(request)


@require_POST
def htmx_template_set_category(request, pk):
    tpl = get_object_or_404(ResponseTemplate, pk=pk)
    cat_id = request.POST.get("category", "")
    tpl.category = TemplateCategory.objects.filter(pk=cat_id).first() if cat_id else None
    tpl.save()
    response = HttpResponse(status=204)
    response["HX-Redirect"] = reverse("dashboard:sales_templates")
    return response


@require_POST
def htmx_prospect_response(request, slug):
    prospect = get_object_or_404(Prospect, slug=slug)
    template_id = request.POST.get("template_id", "")
    notes = request.POST.get("response_notes", "").strip()

    template = None
    if template_id:
        template = ResponseTemplate.objects.filter(pk=template_id).first()

    ProspectResponse.objects.create(
        prospect=prospect,
        template=template,
        notes=notes,
        sent_at=timezone.now(),
    )

    responses = prospect.responses.select_related("template").all()
    return render(request, "dashboard/sales/_prospect_responses.html", {
        "prospect": prospect,
        "responses": responses,
    })


@require_POST
def htmx_prospect_scrape_email(request, slug):
    """Scrape the prospect's website for email and contact person."""
    prospect = get_object_or_404(Prospect, slug=slug)

    if not prospect.website:
        return _toast_response(HttpResponse(""), "error", "Geen website bekend.")

    try:
        info = scrape_contact_info(prospect.website)
    except Exception:
        logger.exception("Contact scrape failed for %s", prospect.website)
        return _toast_response(HttpResponse(""), "error", "Scrape mislukt.")

    if not info.email and not info.contact_first_name:
        return _toast_response(
            HttpResponse(
                '<span class="text-xs text-gray-400">Geen contactinfo gevonden</span>'
            ),
            "warning",
            f"Geen contactinfo gevonden op {prospect.website}",
        )

    update_fields = []
    if info.email and not prospect.email:
        prospect.email = info.email
        update_fields.append("email")
    if info.contact_first_name and not prospect.contact_first_name:
        prospect.contact_first_name = info.contact_first_name
        update_fields.append("contact_first_name")
    if info.contact_last_name and not prospect.contact_last_name:
        prospect.contact_last_name = info.contact_last_name
        update_fields.append("contact_last_name")
    if not prospect.aanhef:
        prospect.aanhef = "Geachte heer/mevrouw"
        update_fields.append("aanhef")
    if update_fields:
        prospect.save(update_fields=update_fields)

    # Build toast message
    found_parts = []
    if info.email:
        found_parts.append(info.email)
    if info.contact_first_name or info.contact_last_name:
        found_parts.append(f"{info.contact_first_name or ''} {info.contact_last_name or ''}".strip())
    toast_msg = "Gevonden: " + ", ".join(found_parts)

    # Re-render the contact fields with updated values
    input_cls = (
        "w-full rounded-xl border-gray-300 text-sm px-4 py-2.5 shadow-sm "
        "focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
    )
    aanhef_options = ""
    for value, label in Prospect.AANHEF_CHOICES:
        selected = ' selected' if prospect.aanhef == value else ''
        aanhef_options += f'<option value="{html_escape(value)}"{selected}>{html_escape(label)}</option>'

    html = f"""
    <div class="grid grid-cols-2 gap-4">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Voornaam</label>
            <input type="text" name="contact_first_name" value="{html_escape(prospect.contact_first_name)}" placeholder="Voornaam" class="{input_cls}">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Achternaam</label>
            <input type="text" name="contact_last_name" value="{html_escape(prospect.contact_last_name)}" placeholder="Achternaam" class="{input_cls}">
        </div>
    </div>
    <div class="grid grid-cols-2 gap-4 mt-4">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <input type="email" name="email" value="{html_escape(prospect.email)}" placeholder="info@bedrijf.nl" class="{input_cls}">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Aanhef</label>
            <select name="aanhef">{aanhef_options}</select>
        </div>
    </div>
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">LinkedIn URL</label>
        <input type="url" name="linkedin_url" value="{html_escape(prospect.linkedin_url)}" placeholder="https://linkedin.com/in/..." class="{input_cls}">
    </div>
    """

    return _toast_response(HttpResponse(html), "success", toast_msg)


def _send_fiscal_summary_email(articles: list[dict], log_callback):
    """Send a summary email after fiscal research completes. Errors are logged but never raised."""
    from accounts.services.email_backend import send_email

    try:
        email_to = os.environ.get("EMAIL_TO", os.environ.get("MS_GRAPH_USER_ID", ""))

        if not email_to:
            logger.warning("EMAIL_TO niet geconfigureerd — fiscale samenvatting niet verzonden")
            return

        article_count = len(articles)
        rows = ""
        for a in articles:
            title = html_escape(a.get("title", "Zonder titel"))
            category = html_escape(a.get("category", "algemeen"))
            rows += f"<tr><td style='padding:4px 8px'>{title}</td><td style='padding:4px 8px'>{category}</td></tr>"

        html_body = f"""\
<html><body>
<h2>Fiscaal onderzoek afgerond</h2>
<p>Er zijn <strong>{article_count}</strong> nieuwe concept-artikelen aangemaakt.</p>
<table border="1" cellpadding="0" cellspacing="0" style="border-collapse:collapse">
<tr><th style="padding:4px 8px">Titel</th><th style="padding:4px 8px">Categorie</th></tr>
{rows}
</table>
<p>Bekijk de artikelen in de <a href="/">Bedrijfsmonitor</a>.</p>
</body></html>"""

        subject = f"Fiscaal onderzoek afgerond — {article_count} nieuwe artikelen"
        plain_text = f"Fiscaal onderzoek afgerond. {article_count} nieuwe concept-artikelen aangemaakt."

        send_email(email_to, subject, plain_text, html_body)
        log_callback("info", "System", f"Samenvattings-e-mail verzonden naar {email_to}")

    except Exception as e:
        logger.warning("Fiscale samenvattings-e-mail kon niet worden verzonden: %s", e)
        log_callback("warning", "System", f"E-mail kon niet worden verzonden: {e}")


# ===================================================================
# Team Builder views
# ===================================================================

from .constants import PROVIDER_CONFIG, SUGGESTED_MODELS
from .tool_registry import get_tool_choices, get_tools_by_category, TOOL_REGISTRY


def _team_detail_context(team):
    """Shared context dict for team_detail and its HTMX partials."""
    active_job = ScanJob.objects.filter(
        team=team, status__in=["pending", "running"]
    ).first()
    if not active_job:
        # Show last completed/failed job so reports remain visible
        active_job = ScanJob.objects.filter(
            team=team, status__in=["completed", "failed"]
        ).first()

    # Provider info for model configuration section
    provider_meta = {
        "gemini": {"label": "Gemini", "border_class": "border-blue-200", "text_class": "text-blue-700"},
        "anthropic": {"label": "Anthropic", "border_class": "border-orange-200", "text_class": "text-orange-700"},
        "openai": {"label": "OpenAI", "border_class": "border-green-200", "text_class": "text-green-700"},
    }
    provider_info = []
    for key, cfg in PROVIDER_CONFIG.items():
        meta = provider_meta.get(key, {})
        provider_info.append({
            "key": key,
            "label": meta.get("label", key),
            "border_class": meta.get("border_class", "border-gray-200"),
            "text_class": meta.get("text_class", "text-gray-700"),
            "has_key": bool(os.environ.get(cfg["env_key"], "")),
            "env_key": cfg["env_key"],
            "models": SUGGESTED_MODELS.get(key, []),
        })

    return {
        "team": team,
        "variables": team.variables.all(),
        "agents": team.agents.all(),
        "manager": team.agents.filter(is_manager=True).first(),
        "workers": team.agents.filter(is_manager=False).order_by("order"),
        "tasks": team.tasks.select_related("agent").prefetch_related("context_tasks"),
        "active_job": active_job,
        "active_job_logs": active_job.logs.all() if active_job else [],
        "task_outputs": active_job.task_outputs.all() if active_job and active_job.status == "completed" else [],
        "tool_choices": get_tool_choices(),
        "tool_choices_grouped": get_tools_by_category(),
        "tool_registry": TOOL_REGISTRY,
        "provider_choices": TeamAgent.PROVIDER_CHOICES,
        "suggested_models": SUGGESTED_MODELS,
        "provider_info": provider_info,
    }


# --- AI Configuration ---

def ai_config(request):
    """AI Configuration page: providers, models, and tools overview."""
    from .tool_registry import get_tools_by_category

    provider_meta = {
        "gemini": {"label": "Gemini", "border_class": "border-blue-200", "text_class": "text-blue-700", "bg_class": "bg-blue-50"},
        "anthropic": {"label": "Anthropic", "border_class": "border-orange-200", "text_class": "text-orange-700", "bg_class": "bg-orange-50"},
        "openai": {"label": "OpenAI", "border_class": "border-green-200", "text_class": "text-green-700", "bg_class": "bg-green-50"},
    }
    provider_info = []
    for key, cfg in PROVIDER_CONFIG.items():
        meta = provider_meta.get(key, {})
        provider_info.append({
            "key": key,
            "label": meta.get("label", key),
            "border_class": meta.get("border_class", "border-gray-200"),
            "text_class": meta.get("text_class", "text-gray-700"),
            "bg_class": meta.get("bg_class", "bg-gray-50"),
            "has_key": bool(os.environ.get(cfg["env_key"], "")),
            "env_key": cfg["env_key"],
            "models": SUGGESTED_MODELS.get(key, []),
        })

    return render(request, "dashboard/ai_config.html", {
        "provider_info": provider_info,
        "tool_categories": get_tools_by_category(),
        "tool_count": len(TOOL_REGISTRY),
    })


# --- Ownership helpers ---

def _user_teams(request):
    """Return teams owned by the current user (or unowned legacy teams)."""
    return Team.objects.filter(Q(owner=request.user) | Q(owner__isnull=True))


def _get_user_team(request, slug):
    """Get a team ensuring the current user has access."""
    return get_object_or_404(Team, slug=slug, owner__in=[request.user, None])


def _user_groups(request):
    """Return prospect groups owned by the current user (or unowned legacy groups)."""
    return ProspectGroup.objects.filter(Q(owner=request.user) | Q(owner__isnull=True))


def _get_user_group(request, slug):
    """Get a prospect group ensuring the current user has access."""
    return get_object_or_404(ProspectGroup, slug=slug, owner__in=[request.user, None])


# --- Team CRUD ---

def team_list(request):
    teams = _user_teams(request).annotate(
        agent_count=db_models.Count("agents"),
        task_count=db_models.Count("tasks"),
    )
    return render(request, "dashboard/teams/team_list.html", {"teams": teams})


@require_POST
def team_create(request):
    name = request.POST.get("name", "").strip()
    if not name:
        return render(request, "dashboard/teams/team_list.html", {
            "teams": Team.objects.all(), "error": "Naam is verplicht.",
        })
    team = Team(name=name, owner=request.user)
    team.save()
    return redirect("dashboard:team_detail", slug=team.slug)


def team_detail(request, slug):
    team = _get_user_team(request, slug)
    ctx = _team_detail_context(team)
    return render(request, "dashboard/teams/team_detail.html", ctx)


@require_POST
def team_delete(request, slug):
    team = _get_user_team(request, slug)
    team.delete()
    messages.success(request, "Team verwijderd")
    return redirect("dashboard:team_list")


@require_POST
def team_bulk_delete(request):
    slugs = request.POST.getlist("slugs")
    if slugs:
        qs = _user_teams(request).filter(slug__in=slugs)
        count = qs.count()
        qs.delete()
        messages.success(request, f"{count} team(s) verwijderd")
    return redirect("dashboard:team_list")


@require_POST
def team_update(request, slug):
    """HTMX: update team header fields."""
    team = _get_user_team(request, slug)
    team.name = request.POST.get("name", team.name).strip() or team.name
    team.description = request.POST.get("description", team.description)
    process = request.POST.get("process", team.process)
    if process in {c[0] for c in Team.PROCESS_CHOICES}:
        team.process = process
    team.save()
    ctx = _team_detail_context(team)
    return render(request, "dashboard/teams/_team_header.html", ctx)


# --- Variable CRUD ---

@require_POST
def team_variable_add(request, slug):
    team = _get_user_team(request, slug)
    name = request.POST.get("name", "").strip()
    if name:
        max_order = team.variables.aggregate(m=db_models.Max("order"))["m"] or 0
        options = []
        options_raw = request.POST.get("options", "").strip()
        if options_raw:
            try:
                options = json.loads(options_raw)
            except (json.JSONDecodeError, ValueError):
                options = []
        TeamVariable.objects.create(
            team=team,
            name=name,
            label=request.POST.get("label", name).strip(),
            description=request.POST.get("description", "").strip(),
            input_type=request.POST.get("input_type", "text"),
            default_value=request.POST.get("default_value", ""),
            options=options,
            required="required" in request.POST,
            order=max_order + 1,
        )
    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_variables.html", ctx)
    return _toast_response(response, "success", "Variabele toegevoegd")


@require_POST
def team_variable_edit(request, slug, pk):
    team = _get_user_team(request, slug)
    var = get_object_or_404(TeamVariable, pk=pk, team=team)
    # Alleen velden updaten die daadwerkelijk in de POST zitten
    if "name" in request.POST:
        var.name = request.POST["name"].strip() or var.name
    if "label" in request.POST:
        var.label = request.POST["label"].strip()
    if "description" in request.POST:
        var.description = request.POST["description"]
    if "input_type" in request.POST:
        var.input_type = request.POST["input_type"]
    if "default_value" in request.POST:
        var.default_value = request.POST["default_value"]
    if "options" in request.POST:
        options_raw = request.POST["options"].strip()
        if options_raw:
            try:
                var.options = json.loads(options_raw)
            except (json.JSONDecodeError, ValueError):
                pass  # Ongeldige JSON, negeer
        else:
            var.options = []
    # required alleen wijzigen bij volledig edit formulier (heeft altijd "name")
    if "name" in request.POST:
        var.required = "required" in request.POST
    var.save()
    ctx = _team_detail_context(team)
    return render(request, "dashboard/teams/_variables.html", ctx)


@require_POST
def team_variable_upload(request, slug, pk):
    """Upload een PDF-bestand en sla het pad op als default_value."""
    import re as _re
    import uuid as _uuid
    from pathlib import Path as _Path

    team = _get_user_team(request, slug)
    var = get_object_or_404(TeamVariable, pk=pk, team=team)

    uploaded = request.FILES.get("file")
    if not uploaded:
        ctx = _team_detail_context(team)
        return _toast_response(
            render(request, "dashboard/teams/_variables.html", ctx),
            "error", "Geen bestand geselecteerd",
        )

    if not uploaded.name.lower().endswith(".pdf"):
        ctx = _team_detail_context(team)
        return _toast_response(
            render(request, "dashboard/teams/_variables.html", ctx),
            "error", "Alleen PDF-bestanden zijn toegestaan",
        )

    if uploaded.size > 50 * 1024 * 1024:
        ctx = _team_detail_context(team)
        return _toast_response(
            render(request, "dashboard/teams/_variables.html", ctx),
            "error", "Bestand is groter dan 50 MB",
        )

    # Verify PDF magic bytes
    first_bytes = uploaded.read(5)
    uploaded.seek(0)
    if not first_bytes.startswith(b"%PDF-"):
        ctx = _team_detail_context(team)
        return _toast_response(
            render(request, "dashboard/teams/_variables.html", ctx),
            "error", "Ongeldig PDF-bestand",
        )

    upload_dir = _Path(settings.MEDIA_ROOT) / "teams" / team.slug
    upload_dir.mkdir(parents=True, exist_ok=True)
    # Sanitize: verwijder alleen path-gevaarlijke tekens, behoud spaties en unicode
    clean_name = _re.sub(r'[<>:"/\\|?*]', '_', uploaded.name)
    safe_name = f"{_uuid.uuid4().hex[:8]}_{clean_name}"
    file_path = upload_dir / safe_name
    with open(file_path, "wb") as f:
        for chunk in uploaded.chunks():
            f.write(chunk)
    var.default_value = str(file_path)
    var.save()

    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_variables.html", ctx)
    return _toast_response(response, "success", f"Bestand geupload: {uploaded.name}")


@require_POST
def team_variable_delete(request, slug, pk):
    team = _get_user_team(request, slug)
    TeamVariable.objects.filter(pk=pk, team=team).delete()
    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_variables.html", ctx)
    return _toast_response(response, "success", "Variabele verwijderd")


# --- Agent CRUD ---

@require_POST
def team_agent_add(request, slug):
    team = _get_user_team(request, slug)
    role = request.POST.get("role", "").strip()
    if role:
        max_order = team.agents.aggregate(m=db_models.Max("order"))["m"] or 0
        valid_tool_ids = set(TOOL_REGISTRY.keys())
        tools = [t for t in request.POST.getlist("tools") if t in valid_tool_ids]
        is_manager = "is_manager" in request.POST
        if is_manager:
            tools = []  # CrewAI: manager agents cannot have tools
        max_iter = min(_safe_int(request.POST.get("max_iter", 25), 25), 200)
        with transaction.atomic():
            if is_manager:
                team.agents.update(is_manager=False)
            TeamAgent.objects.create(
                team=team,
                order=max_order + 1,
                role=role,
                goal=request.POST.get("goal", ""),
                backstory=request.POST.get("backstory", ""),
                llm_provider=request.POST.get("llm_provider", "gemini"),
                llm_model=request.POST.get("llm_model", "gemini-3-flash-preview"),
                tools=tools,
                max_iter=max_iter,
                verbose=True,
                is_manager=is_manager,
            )
    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_agents_and_tasks.html", ctx)
    return _toast_response(response, "success", "Agent toegevoegd")


@require_POST
def team_agent_edit(request, slug, pk):
    team = _get_user_team(request, slug)
    agent = get_object_or_404(TeamAgent, pk=pk, team=team)
    agent.role = request.POST.get("role", agent.role).strip() or agent.role
    agent.goal = request.POST.get("goal", agent.goal)
    agent.backstory = request.POST.get("backstory", agent.backstory)
    agent.llm_provider = request.POST.get("llm_provider", agent.llm_provider)
    agent.llm_model = request.POST.get("llm_model", agent.llm_model)
    valid_tool_ids = set(TOOL_REGISTRY.keys())
    agent.tools = [t for t in request.POST.getlist("tools") if t in valid_tool_ids]
    agent.max_iter = min(_safe_int(request.POST.get("max_iter", agent.max_iter), agent.max_iter), 200)
    agent.is_manager = "is_manager" in request.POST
    if agent.is_manager:
        agent.tools = []  # CrewAI: manager agents cannot have tools
    with transaction.atomic():
        if agent.is_manager:
            team.agents.exclude(pk=agent.pk).update(is_manager=False)
        agent.save()
    ctx = _team_detail_context(team)
    return render(request, "dashboard/teams/_agents_and_tasks.html", ctx)


@require_POST
def team_agent_delete(request, slug, pk):
    team = _get_user_team(request, slug)
    TeamAgent.objects.filter(pk=pk, team=team).delete()
    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_agents_and_tasks.html", ctx)
    return _toast_response(response, "success", "Agent verwijderd")


@require_POST
def team_agent_set_manager(request, slug, pk):
    team = _get_user_team(request, slug)
    agent = get_object_or_404(TeamAgent, pk=pk, team=team)
    with transaction.atomic():
        team.agents.update(is_manager=False)
        agent.is_manager = True
        agent.tools = []  # CrewAI: manager agents cannot have tools
        agent.save(update_fields=["is_manager", "tools"])
    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_agents_and_tasks.html", ctx)
    return _toast_response(response, "success", f"{agent.role} is nu hoofdagent")


# --- Task CRUD ---

@require_POST
def team_task_add(request, slug):
    team = _get_user_team(request, slug)
    description = request.POST.get("description", "").strip()
    agent_pk = request.POST.get("agent", "")
    if description and agent_pk:
        agent = get_object_or_404(TeamAgent, pk=agent_pk, team=team)
        max_order = team.tasks.aggregate(m=db_models.Max("order"))["m"] or 0
        task = TeamTask.objects.create(
            team=team,
            order=max_order + 1,
            description=description,
            expected_output=request.POST.get("expected_output", ""),
            agent=agent,
        )
        ctx_pks = request.POST.getlist("context_tasks")
        if ctx_pks:
            task.context_tasks.set(TeamTask.objects.filter(pk__in=ctx_pks, team=team))
    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_agents_and_tasks.html", ctx)
    return _toast_response(response, "success", "Taak toegevoegd")


@require_POST
def team_task_edit(request, slug, pk):
    team = _get_user_team(request, slug)
    task = get_object_or_404(TeamTask, pk=pk, team=team)
    task.description = request.POST.get("description", task.description)
    task.expected_output = request.POST.get("expected_output", task.expected_output)
    agent_pk = request.POST.get("agent", "")
    if agent_pk:
        task.agent = get_object_or_404(TeamAgent, pk=agent_pk, team=team)
    task.save()
    ctx_pks = request.POST.getlist("context_tasks")
    task.context_tasks.set(TeamTask.objects.filter(pk__in=ctx_pks, team=team))
    ctx = _team_detail_context(team)
    return render(request, "dashboard/teams/_agents_and_tasks.html", ctx)


@require_POST
def team_task_delete(request, slug, pk):
    team = _get_user_team(request, slug)
    TeamTask.objects.filter(pk=pk, team=team).delete()
    ctx = _team_detail_context(team)
    response = render(request, "dashboard/teams/_agents_and_tasks.html", ctx)
    return _toast_response(response, "success", "Taak verwijderd")


# --- Team Run ---

@ratelimit(key="user_or_ip", rate="5/h", method="POST", block=True)
@require_POST
def team_run(request, slug):
    """Start a team run with provided variables."""
    team = _get_user_team(request, slug)

    # Collect variable values from saved default_values
    # File uploads are handled separately via team_variable_upload
    run_variables = {}
    for var in team.variables.all():
        run_variables[var.name] = var.default_value

    with transaction.atomic():
        active = ScanJob.objects.select_for_update().filter(
            team=team, status__in=["pending", "running"]
        ).first()
        if active:
            ctx = _team_detail_context(team)
            return render(request, "dashboard/teams/_run_status.html", ctx)

        job = ScanJob.objects.create(
            status="pending",
            job_type="custom",
            team=team,
            run_variables=run_variables,
            progress_message=f"{team.name} wordt gestart...",
        )

    _scan_executor.submit(_run_custom_team_background, job.pk, team.pk, run_variables)

    ctx = _team_detail_context(team)
    ctx["active_job"] = job
    ctx["active_job_logs"] = []
    return render(request, "dashboard/teams/_run_status.html", ctx)


def team_run_status(request, slug, pk):
    """HTMX polling endpoint for team run progress."""
    team = _get_user_team(request, slug)
    job = get_object_or_404(ScanJob, pk=pk)
    logs = job.logs.all()

    stale = False
    last_activity_seconds = None
    if job.status == "running":
        last_log = logs.order_by("-created_at").first()
        if last_log:
            last_activity_seconds = int((timezone.now() - last_log.created_at).total_seconds())
            if last_activity_seconds > 600:
                stale = True

    ctx = _team_detail_context(team)
    ctx.update({
        "active_job": job,
        "active_job_logs": logs,
        "stale": stale,
        "last_activity_seconds": last_activity_seconds,
    })
    return render(request, "dashboard/teams/_run_status.html", ctx)


@require_POST
def team_run_stop(request, slug, pk):
    """Stop a running team job."""
    team = _get_user_team(request, slug)
    job = get_object_or_404(ScanJob, pk=pk)
    if job.status in ("pending", "running"):
        job.status = "failed"
        job.progress_message = "Run handmatig gestopt"
        job.finished_at = timezone.now()
        job.save()
        ScanLog.objects.create(
            job=job, event_type="error", agent_name="System",
            message="Team run gestopt door gebruiker",
        )
    ctx = _team_detail_context(team)
    ctx["active_job"] = job
    ctx["active_job_logs"] = job.logs.all()
    response = render(request, "dashboard/teams/_run_status.html", ctx)
    return _toast_response(response, "warning", "Team run gestopt")


def team_run_dismiss(request, slug, pk):
    """Dismiss the current job result and show the run form again."""
    team = _get_user_team(request, slug)
    ctx = _team_detail_context(team)
    ctx["active_job"] = None
    ctx["active_job_logs"] = []
    ctx["task_outputs"] = []
    return render(request, "dashboard/teams/_run_status.html", ctx)


def _pdf_safe_text(text):
    """Replace emoji characters with text equivalents for PDF rendering."""
    return (text
        .replace("\u2705", "[OK]")       # ✅
        .replace("\u274c", "[FOUT]")     # ❌
        .replace("\u26a0\ufe0f", "[LET OP]")  # ⚠️
        .replace("\u26a0", "[LET OP]")   # ⚠
        .replace("\u2713", "[OK]")       # ✓
        .replace("\u2717", "[FOUT]")     # ✗
        .replace("\u2714", "[OK]")       # ✔
        .replace("\u2718", "[FOUT]")     # ✘
    )


def team_run_pdf(request, slug, pk):
    """Generate a PDF report from task outputs of a completed team run."""
    import weasyprint
    from dashboard.templatetags.report_filters import render_markdown as md_filter

    team = _get_user_team(request, slug)
    job = get_object_or_404(ScanJob, pk=pk, team=team, status="completed")
    outputs = job.task_outputs.all()

    if not outputs:
        return HttpResponse("Geen rapporten beschikbaar voor deze run.", status=404)

    # Build HTML document for PDF
    sections_html = ""
    for to in outputs:
        rendered = md_filter(_pdf_safe_text(to.output))
        sections_html += f"""
        <div class="section">
            <div class="section-header">
                <span class="badge">{to.task_order + 1}</span>
                <span class="agent-name">{to.agent_name}</span>
            </div>
            <div class="content">{rendered}</div>
        </div>
        """

    finished = job.finished_at.strftime("%d-%m-%Y %H:%M") if job.finished_at else ""
    html_content = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
    @page {{
        size: A4; margin: 2cm 2.5cm;
        @bottom-center {{ content: counter(page) " / " counter(pages); font-size: 9px; color: #999; }}
    }}
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 11pt; color: #1a1a2e; line-height: 1.6; }}
    .header {{ border-bottom: 3px solid #4338ca; padding-bottom: 12px; margin-bottom: 24px; }}
    .header h1 {{ font-size: 20pt; color: #312e81; margin: 0 0 4px 0; }}
    .header .meta {{ font-size: 9pt; color: #6b7280; }}
    .section {{ margin-bottom: 24px; border-top: 1px solid #e2e8f0; padding-top: 16px; }}
    .section:first-child {{ border-top: none; padding-top: 0; }}
    .section-header {{ background: #f1f5f9; padding: 8px 14px; border-radius: 6px; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; page-break-after: avoid; }}
    .badge {{ background: #e0e7ff; color: #4338ca; font-weight: 700; width: 24px; height: 24px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; font-size: 10pt; }}
    .agent-name {{ font-weight: 600; font-size: 11pt; color: #1e293b; }}
    .content {{ padding: 0 4px; page-break-before: avoid; }}
    .content h1 {{ font-size: 15pt; color: #312e81; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-top: 16px; }}
    .content h2 {{ font-size: 13pt; color: #4338ca; margin-top: 14px; }}
    .content h3 {{ font-size: 11pt; color: #475569; margin-top: 12px; }}
    .content p {{ margin: 6px 0; }}
    .content ul, .content ol {{ padding-left: 20px; margin: 6px 0; }}
    .content li {{ margin: 3px 0; }}
    .content table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 10pt; }}
    .content th {{ background: #f8fafc; font-weight: 600; border-bottom: 2px solid #e2e8f0; padding: 6px 8px; text-align: left; }}
    .content td {{ padding: 5px 8px; border-bottom: 1px solid #f1f5f9; }}
    .content code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-size: 9pt; }}
    .content pre {{ background: #f8fafc; padding: 10px; border-radius: 6px; font-size: 9pt; overflow-wrap: break-word; white-space: pre-wrap; }}
</style>
</head><body>
    <div class="header">
        <h1>{team.name}</h1>
        <div class="meta">Rapport gegenereerd op {finished} &bull; {outputs.count()} onderdelen</div>
    </div>
    {sections_html}
</body></html>"""

    pdf = weasyprint.HTML(string=html_content).write_pdf()
    response = HttpResponse(pdf, content_type="application/pdf")
    safe_name = team.slug
    response["Content-Disposition"] = f'inline; filename="{safe_name}-rapport.pdf"'
    return response


# --- Background team run ---

def _run_custom_team_background(job_pk: int, team_pk: int, run_variables: dict):
    """Run a custom Team crew in a background thread."""
    import sys
    # Fix stdout if closed by a previous CrewAI run
    try:
        sys.stdout.isatty()
    except (ValueError, AttributeError, OSError):
        sys.stdout = sys.__stdout__
    try:
        import django
        django.setup()
    except Exception:
        logger.error("django.setup() failed in _run_custom_team_background", exc_info=True)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dashboard_scanjob SET status='failed', error_message='Django setup failed' WHERE id=%s",
                    [job_pk],
                )
        except Exception:
            pass
        return

    close_old_connections()
    from dashboard.models import ScanJob, ScanLog, Team

    job = ScanJob.objects.get(pk=job_pk)
    job.status = "running"
    job.progress_message = "Agents worden opgestart..."
    job.save(update_fields=["status", "progress_message"])

    def _is_cancelled():
        try:
            return ScanJob.objects.filter(pk=job_pk, status="failed").exists()
        except Exception:
            return False

    def log_callback(event_type, agent_name, message):
        try:
            if _is_cancelled():
                return
            ScanLog.objects.create(
                job_id=job_pk,
                event_type=event_type,
                agent_name=agent_name or "",
                message=message or "",
            )
            if event_type in ("agent", "task_done", "start"):
                short = (message or "")[:295]
                ScanJob.objects.filter(pk=job_pk).update(progress_message=short)
        except Exception:
            logger.error("Error in team log_callback", exc_info=True)

    try:
        team = Team.objects.get(pk=team_pk)
        log_callback("start", "System", f"Team '{team.name}' gestart...")

        from dashboard.crew_builder import build_crew_from_team

        # Build callbacks
        agent_roles = list(team.agents.order_by("order").values_list("role", flat=True))
        task_index = [0]
        task_lock = threading.Lock()

        def step_cb(step_output):
            try:
                tool = getattr(step_output, "tool", "")
                thought = getattr(step_output, "thought", "") or getattr(step_output, "log", "")
                output = getattr(step_output, "output", "")
                with task_lock:
                    idx = min(task_index[0], len(agent_roles) - 1)
                agent_name = agent_roles[idx] if agent_roles else ""

                if tool:
                    log_callback("tool", agent_name, f"Tool: {tool}")
                elif thought and not output:
                    log_callback("thought", agent_name, str(thought)[:300])
                elif output:
                    log_callback("result", agent_name, str(output)[:400])
            except Exception:
                logger.error("Error in team step_cb", exc_info=True)

        def task_cb(task_output):
            try:
                with task_lock:
                    idx = task_index[0]
                    task_index[0] = idx + 1
                    next_idx = task_index[0]
                agent_name = agent_roles[idx] if idx < len(agent_roles) else "Agent"
                raw = str(getattr(task_output, "raw", ""))
                summary = raw[:300]
                log_callback("task_done", agent_name, f"Taak afgerond\n{summary}")

                # Store full task output for report display
                TaskOutput.objects.create(
                    job_id=job_pk,
                    task_order=idx,
                    agent_name=agent_name,
                    task_description=str(getattr(task_output, "description", ""))[:500],
                    output=raw,
                )

                if next_idx < len(agent_roles):
                    next_agent = agent_roles[next_idx]
                    log_callback("agent", next_agent, f"Agent {next_idx + 1}/{len(agent_roles)} gestart")
                    ScanJob.objects.filter(pk=job_pk).update(
                        active_agent=next_agent,
                        tasks_completed=next_idx,
                        progress_message=f"Agent {next_idx + 1}/{len(agent_roles)}: {next_agent}",
                    )
                else:
                    ScanJob.objects.filter(pk=job_pk).update(tasks_completed=next_idx)
            except Exception:
                logger.error("Error in team task_cb", exc_info=True)

        crew, agents_list = build_crew_from_team(
            team, run_variables,
            step_callback=step_cb, task_callback=task_cb,
        )

        if agent_roles:
            log_callback("agent", agent_roles[0], f"Agent 1/{len(agent_roles)} gestart")
            ScanJob.objects.filter(pk=job_pk).update(
                active_agent=agent_roles[0],
                progress_message=f"Agent 1/{len(agent_roles)}: {agent_roles[0]}",
            )

        import io
        import sys
        with _stdout_lock:
            original_stdout = sys.stdout
            wrapper = None
            try:
                wrapper = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
                )
                sys.stdout = wrapper
            except AttributeError:
                pass

            try:
                result = crew.kickoff()
            finally:
                if wrapper is not None:
                    try:
                        wrapper.detach()  # Prevent closing the underlying buffer
                    except Exception:
                        pass
                sys.stdout = original_stdout

        raw_output = str(result.raw) if hasattr(result, "raw") else str(result)

        # Extract token usage (was missing for custom teams)
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0
        if hasattr(result, "token_usage"):
            usage = result.token_usage
            input_tokens = getattr(usage, "prompt_tokens", 0) or 0
            output_tokens = getattr(usage, "completion_tokens", 0) or 0
            total_tokens = getattr(usage, "total_tokens", 0) or (input_tokens + output_tokens)

        # Log API usage (always, even with 0 tokens)
        first_agent = team.agents.order_by("order").first()
        provider = first_agent.llm_provider if first_agent else "gemini"
        model_name = first_agent.llm_model if first_agent else ""

        try:
            from dashboard.services.api_usage import log_llm_usage
            log_llm_usage(
                service=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model_name=model_name,
                job_pk=job_pk,
                description=f"Custom team: {team.name}",
            )
        except Exception:
            logger.warning("Could not log API usage for custom team", exc_info=True)

        job.status = "completed"
        job.progress_message = f"Team '{team.name}' afgerond"
        job.active_agent = ""
        job.tasks_completed = len(agent_roles)
        job.token_count = total_tokens
        job.finished_at = timezone.now()
        job.save()
        log_callback("result", "System", f"Team run afgerond.\n{raw_output[:500]}")

    except Exception as e:
        logger.error("Team run failed (job=%s, team=%s)", job_pk, team_pk, exc_info=True)
        job.status = "failed"
        logger.exception("Job %s failed", job.pk)
        job.error_message = "Er is een fout opgetreden. Controleer de logs voor details."
        job.progress_message = "Team run mislukt"
        job.finished_at = timezone.now()
        job.save()
        log_callback("error", "System", f"Team run mislukt: {type(e).__name__}")
    finally:
        close_old_connections()


# ---------------------------------------------------------------------------
# WWFT Compliance
# ---------------------------------------------------------------------------

def compliance_home(request):
    sections = ComplianceSection.objects.all()
    updated_count = sections.filter(status="updated").count()

    return render(request, "dashboard/compliance/home.html", {
        "sections": sections,
        "total_sections": sections.count(),
        "updated_count": updated_count,
    })


SECTION_SEARCH_TERMS = {
    "wettelijke_basis": "Wwft wetswijziging",
    "clientenonderzoek": "Wwft cliëntenonderzoek identificatie",
    "risicobeleid": "Wwft risicobeleid SIRA",
    "pep_sancties": "PEP sanctielijst Wwft",
    "verscherpt_onderzoek": "verscherpt cliëntenonderzoek EDD",
    "meldplicht": "FIU meldplicht ongebruikelijke transactie",
    "herbeoordeling": "Wwft voortdurende controle herbeoordeling",
    "compliance_infra": "Wwft compliance officer opleiding",
    "bft_bevindingen": "BFT inspectie bevindingen toezicht",
    "actuele_wetgeving": "Wwft AMLD wijziging 2025 2026",
}


@require_POST
@ratelimit(key="ip", rate="10/m", method="POST")
def compliance_section_check(request, key):
    section = get_object_or_404(ComplianceSection, key=key)

    # Don't start a new check if one is already running
    if section.last_check_job and section.last_check_job.status in ("pending", "running"):
        return render(request, "dashboard/compliance/_section_status.html", {
            "section": section,
            "job": section.last_check_job,
            "logs": section.last_check_job.logs.all(),
        })

    job = ScanJob.objects.create(
        status="pending",
        job_type="compliance",
        run_variables={"section_key": key},
        progress_message=f"Compliance check starten voor {section.title}...",
    )

    section.status = "checking"
    section.last_check_job = job
    section.save(update_fields=["status", "last_check_job"])

    _scan_executor.submit(
        _run_compliance_section_background, job.pk, section.pk
    )

    return render(request, "dashboard/compliance/_section_status.html", {
        "section": section,
        "job": job,
        "logs": [],
    })


def compliance_section_status(request, key, pk):
    section = get_object_or_404(ComplianceSection, key=key)
    job = get_object_or_404(ScanJob, pk=pk)
    logs = job.logs.all()

    # Stale detection: if running for more than 600s, mark as failed
    if job.status == "running" and job.created_at:
        elapsed = (timezone.now() - job.created_at).total_seconds()
        if elapsed > 600:
            job.status = "failed"
            job.error_message = "Timeout: check duurde langer dan 10 minuten"
            job.finished_at = timezone.now()
            job.save()
            section.status = "error"
            section.save(update_fields=["status"])

    # If job completed, refresh section from DB
    if job.status == "completed":
        section.refresh_from_db()

    return render(request, "dashboard/compliance/_section_status.html", {
        "section": section,
        "job": job,
        "logs": logs,
    })


@require_POST
def compliance_section_stop(request, key, pk):
    section = get_object_or_404(ComplianceSection, key=key)
    job = get_object_or_404(ScanJob, pk=pk)

    if job.status in ("pending", "running"):
        job.status = "failed"
        job.error_message = "Handmatig gestopt door gebruiker"
        job.finished_at = timezone.now()
        job.save()
        section.status = "default"
        section.save(update_fields=["status"])

    response = render(request, "dashboard/compliance/_section_status.html", {
        "section": section,
        "job": job,
        "logs": job.logs.all(),
    })
    return _toast_response(response, "warning", "Controle gestopt")


@require_POST
@ratelimit(key="ip", rate="10/m", method="POST")
def compliance_legislation_search(request):
    search_term = request.POST.get("search_term", "").strip()
    if not search_term:
        return render(request, "dashboard/compliance/_legislation_search_status.html", {
            "error": "Voer een zoekterm in.",
        })

    job = ScanJob.objects.create(
        status="pending",
        job_type="compliance",
        run_variables={"search_term": search_term},
        progress_message=f"Wetgeving zoeken: {search_term}...",
    )

    _scan_executor.submit(
        _run_compliance_section_background, job.pk, None, search_term
    )

    return render(request, "dashboard/compliance/_legislation_search_status.html", {
        "job": job,
        "logs": [],
        "search_term": search_term,
    })


@require_POST
@ratelimit(key="ip", rate="5/m", method="POST")
def compliance_investigate(request):
    """Start a full WWFT person/entity investigation."""
    entity_name = request.POST.get("entity_name", "").strip()
    if not entity_name:
        return render(request, "dashboard/compliance/_investigation_status.html", {
            "error": "Voer een naam in om te onderzoeken.",
        })

    # Don't start if one is already running
    active = ScanJob.objects.filter(
        status__in=["pending", "running"], job_type="compliance",
        run_variables__contains={"investigation_type": "person"},
    ).first()
    if active:
        return render(request, "dashboard/compliance/_investigation_status.html", {
            "job": active,
            "logs": active.logs.all(),
            "entity_name": entity_name,
        })

    job = ScanJob.objects.create(
        status="pending",
        job_type="compliance",
        run_variables={"entity_name": entity_name, "investigation_type": "person"},
        progress_message=f"Onderzoek starten voor {entity_name}...",
    )

    _scan_executor.submit(_run_compliance_investigation_background, job.pk, entity_name)

    return render(request, "dashboard/compliance/_investigation_status.html", {
        "job": job,
        "logs": [],
        "entity_name": entity_name,
    })


def compliance_investigate_status(request, pk):
    """HTMX polling endpoint for investigation progress."""
    job = get_object_or_404(ScanJob, pk=pk)
    logs = job.logs.all()
    entity_name = (job.run_variables or {}).get("entity_name", "")

    # Stale detection
    if job.status == "running" and job.created_at:
        elapsed = (timezone.now() - job.created_at).total_seconds()
        if elapsed > 900:
            job.status = "failed"
            job.error_message = "Timeout: onderzoek duurde langer dan 15 minuten"
            job.finished_at = timezone.now()
            job.save()

    return render(request, "dashboard/compliance/_investigation_status.html", {
        "job": job,
        "logs": logs,
        "entity_name": entity_name,
    })


@require_POST
def compliance_investigate_stop(request, pk):
    """Stop a running investigation."""
    job = get_object_or_404(ScanJob, pk=pk)
    if job.status in ("pending", "running"):
        job.status = "failed"
        job.error_message = "Handmatig gestopt door gebruiker"
        job.finished_at = timezone.now()
        job.save()

    response = render(request, "dashboard/compliance/_investigation_status.html", {
        "job": job,
        "logs": job.logs.all(),
        "entity_name": (job.run_variables or {}).get("entity_name", ""),
    })
    return _toast_response(response, "warning", "Onderzoek gestopt")


def compliance_archive(request):
    """Overview of all completed compliance checks."""
    reports = ComplianceReport.objects.all()

    type_filter = request.GET.get("type", "")
    if type_filter:
        reports = reports.filter(report_type=type_filter)

    paginator = Paginator(reports, 20)
    page = request.GET.get("page")
    reports_page = paginator.get_page(page)

    return render(request, "dashboard/compliance/archive.html", {
        "reports": reports_page,
        "type_filter": type_filter,
        "report_types": ComplianceReport.REPORT_TYPES,
    })


def compliance_report_detail(request, pk):
    """Detail view for a single compliance report."""
    report = get_object_or_404(ComplianceReport, pk=pk)
    logs = report.job.logs.all() if report.job else []
    return render(request, "dashboard/compliance/report_detail.html", {
        "report": report,
        "logs": logs,
    })


@require_POST
def compliance_section_edit(request, key):
    """Save an inline edit of a compliance section (title + body)."""
    section = get_object_or_404(ComplianceSection, key=key)
    new_body = request.POST.get("body", "").strip()
    new_title = request.POST.get("title", "").strip()

    if new_body and new_body != section.body:
        ComplianceSectionVersion.objects.create(
            section=section, body=section.body, changed_by="user",
        )
        section.body = new_body
    if new_title:
        section.title = new_title
    section.save()

    return render(request, "dashboard/compliance/_section_card.html", {"section": section})


def compliance_section_edit_form(request, key):
    """Return the inline edit form partial for a section."""
    section = get_object_or_404(ComplianceSection, key=key)
    return render(request, "dashboard/compliance/_section_edit_form.html", {"section": section})


def compliance_section_card(request, key):
    """Return a single section card partial (used after HTMX swap)."""
    section = get_object_or_404(ComplianceSection, key=key)
    return render(request, "dashboard/compliance/_section_card.html", {"section": section})


@require_POST
def compliance_section_add(request):
    """Add a new compliance section."""
    from django.db.models import Max
    from django.utils.text import slugify

    title = request.POST.get("title", "").strip()
    if not title:
        sections = ComplianceSection.objects.all()
        return render(request, "dashboard/compliance/_section_list.html", {
            "sections": sections, "add_error": "Vul een titel in.",
        })

    key = slugify(title)[:50]
    body = request.POST.get("body", "").strip() or f"Inhoud voor {title}."
    max_order = ComplianceSection.objects.aggregate(m=Max("order"))["m"] or 0

    ComplianceSection.objects.create(key=key, title=title, body=body, order=max_order + 1)

    sections = ComplianceSection.objects.all()
    return render(request, "dashboard/compliance/_section_list.html", {"sections": sections})


def _run_compliance_section_background(job_pk: int, section_pk: int | None, search_term: str | None = None):
    """Run a targeted WWFT compliance check: direct tool call + LLM summary."""
    try:
        import django
        django.setup()
    except Exception:
        logger.error("django.setup() failed in _run_compliance_section_background", exc_info=True)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dashboard_scanjob SET status='failed', error_message='Django setup failed' WHERE id=%s",
                    [job_pk],
                )
        except Exception:
            pass
        return

    close_old_connections()
    from dashboard.models import ComplianceReport, ComplianceSection, ComplianceSectionVersion, ScanJob, ScanLog

    job = ScanJob.objects.get(pk=job_pk)
    job.status = "running"
    job.progress_message = "Wetgeving ophalen..."
    job.save(update_fields=["status", "progress_message"])

    section = None
    if section_pk:
        section = ComplianceSection.objects.get(pk=section_pk)

    def log_callback(event_type, agent_name, message):
        try:
            if ScanJob.objects.filter(pk=job_pk, status="failed").exists():
                return
            ScanLog.objects.create(
                job_id=job_pk, event_type=event_type,
                agent_name=agent_name or "", message=message or "",
            )
            if event_type in ("start", "tool", "result"):
                ScanJob.objects.filter(pk=job_pk).update(progress_message=(message or "")[:295])
        except Exception:
            logger.error("Error in compliance log_callback", exc_info=True)

    try:
        # Determine search term
        if not search_term and section:
            search_term = SECTION_SEARCH_TERMS.get(section.key, section.title)

        if not search_term:
            raise ValueError("Geen zoekterm bepaald voor deze check")

        log_callback("start", "System", f"Wetgeving ophalen voor: {search_term}")

        # 1. Direct tool call
        from compliance.tools import WWFTLegislationFetcherTool
        tool = WWFTLegislationFetcherTool()
        log_callback("tool", "WWFTLegislationFetcher", f"Zoeken: {search_term}")
        tool_result = tool._run(search_term)
        log_callback("info", "WWFTLegislationFetcher", f"Resultaten opgehaald ({len(tool_result)} tekens)")

        # 2. LLM summary
        section_title = section.title if section else search_term
        log_callback("info", "LLM", "Samenvatting genereren...")
        ScanJob.objects.filter(pk=job_pk).update(progress_message="AI samenvatting genereren...")

        current_body = section.body if section else ""
        summary = _summarize_with_llm(tool_result, section_title, current_body)
        log_callback("result", "LLM", summary[:500])

        # 3. Update section if applicable — overwrite body, save old version
        if section:
            ComplianceSectionVersion.objects.create(
                section=section, body=section.body, changed_by="ai",
            )
            section.body = summary[:10000]
            section.status = "updated"
            section.last_checked = timezone.now()
            section.save(update_fields=["body", "status", "last_checked"])

        # 4. Archive the result
        report_type = "section_check" if section else "legislation_search"
        ComplianceReport.objects.create(
            report_type=report_type,
            entity_name=search_term,
            section=section,
            job=job,
            summary=summary[:5000],
        )

        job.status = "completed"
        job.progress_message = "Compliance check afgerond"
        job.finished_at = timezone.now()
        job.save()

    except Exception as e:
        logger.error("Compliance section check failed (job=%s)", job_pk, exc_info=True)
        job.status = "failed"
        logger.exception("Job %s failed", job.pk)
        job.error_message = "Er is een fout opgetreden. Controleer de logs voor details."
        job.progress_message = "Check mislukt"
        job.finished_at = timezone.now()
        job.save()
        if section:
            section.status = "error"
            section.save(update_fields=["status"])
        log_callback("error", "System", f"Check mislukt: {type(e).__name__}")
    finally:
        close_old_connections()


def _summarize_with_llm(tool_result: str, section_title: str, current_body: str = "") -> str:
    """Send tool result to Gemini LLM to rewrite the section body with up-to-date info."""
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return f"Geen Gemini API key geconfigureerd.\n\nRuwe resultaten:\n{tool_result[:3000]}"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    if current_body:
        prompt = (
            f"Je bent een WWFT compliance expert. Hieronder staat de huidige sectie-tekst van '{section_title}' "
            f"en nieuwe zoekresultaten. Herschrijf de sectie-tekst zodat deze actueel is. "
            f"Behoud de structuur en schrijfstijl van de bestaande tekst, maar verwerk de nieuwe informatie erin. "
            f"Schrijf in het Nederlands. Gebruik markdown opmaak met kopjes en bullet points.\n\n"
            f"--- HUIDIGE TEKST ---\n{current_body[:3000]}\n\n"
            f"--- NIEUWE ZOEKRESULTATEN ---\n{tool_result[:4000]}"
        )
    else:
        prompt = (
            f"Je bent een WWFT compliance expert. Vat de volgende zoekresultaten samen in het Nederlands, "
            f"gericht op '{section_title}'. Geef concrete updates en actiepunten.\n"
            f"Gebruik markdown opmaak met kopjes en bullet points.\n\n"
            f"Zoekresultaten:\n{tool_result[:4000]}"
        )

    response = model.generate_content(prompt)
    return response.text or "Geen samenvatting gegenereerd."


def _run_compliance_investigation_background(job_pk: int, entity_name: str):
    """Run a full WWFT compliance investigation for a person/entity in a background thread."""
    try:
        import django
        django.setup()
    except Exception:
        logger.error("django.setup() failed in _run_compliance_investigation_background", exc_info=True)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dashboard_scanjob SET status='failed', error_message='Django setup failed' WHERE id=%s",
                    [job_pk],
                )
        except Exception:
            pass
        return

    close_old_connections()
    from dashboard.models import ComplianceReport, ScanJob, ScanLog, Team

    job = ScanJob.objects.get(pk=job_pk)
    job.status = "running"
    job.progress_message = "Onderzoek wordt opgestart..."
    job.save(update_fields=["status", "progress_message"])

    def _is_cancelled():
        try:
            return ScanJob.objects.filter(pk=job_pk, status="failed").exists()
        except Exception:
            return False

    def log_callback(event_type, agent_name, message):
        try:
            if _is_cancelled():
                return
            ScanLog.objects.create(
                job_id=job_pk, event_type=event_type,
                agent_name=agent_name or "", message=message or "",
            )
            if event_type in ("agent", "task_done", "start"):
                ScanJob.objects.filter(pk=job_pk).update(progress_message=(message or "")[:295])
        except Exception:
            logger.error("Error in investigation log_callback", exc_info=True)

    try:
        team = Team.objects.filter(slug="wwft-compliance").first()
        if not team:
            raise ValueError("WWFT Compliance team niet gevonden. Voer 'python manage.py seed_teams' uit.")

        log_callback("start", "System", f"Persoonsonderzoek gestart voor: {entity_name}")

        from dashboard.crew_builder import build_crew_from_team

        agent_roles = list(team.agents.order_by("order").values_list("role", flat=True))
        task_index = [0]
        task_lock = threading.Lock()

        def step_cb(step_output):
            try:
                tool = getattr(step_output, "tool", "")
                thought = getattr(step_output, "thought", "") or getattr(step_output, "log", "")
                output = getattr(step_output, "output", "")
                with task_lock:
                    idx = min(task_index[0], len(agent_roles) - 1)
                agent_name = agent_roles[idx] if agent_roles else ""
                if tool:
                    log_callback("tool", agent_name, f"Tool: {tool}")
                elif thought and not output:
                    log_callback("thought", agent_name, str(thought)[:300])
                elif output:
                    log_callback("result", agent_name, str(output)[:400])
            except Exception:
                logger.error("Error in investigation step_cb", exc_info=True)

        def task_cb(task_output):
            try:
                with task_lock:
                    idx = task_index[0]
                    task_index[0] = idx + 1
                    next_idx = task_index[0]
                agent_name = agent_roles[idx] if idx < len(agent_roles) else "Agent"
                summary = str(getattr(task_output, "raw", ""))[:300]
                log_callback("task_done", agent_name, f"Taak afgerond\n{summary}")
                if next_idx < len(agent_roles):
                    next_agent = agent_roles[next_idx]
                    log_callback("agent", next_agent, f"Agent {next_idx + 1}/{len(agent_roles)} gestart")
                    ScanJob.objects.filter(pk=job_pk).update(
                        active_agent=next_agent, tasks_completed=next_idx,
                        progress_message=f"Agent {next_idx + 1}/{len(agent_roles)}: {next_agent}",
                    )
                else:
                    ScanJob.objects.filter(pk=job_pk).update(tasks_completed=next_idx)
            except Exception:
                logger.error("Error in investigation task_cb", exc_info=True)

        run_variables = {"entity_name": entity_name, "investigation_type": "person"}
        crew, agents_list = build_crew_from_team(
            team, run_variables, step_callback=step_cb, task_callback=task_cb,
        )

        if agent_roles:
            log_callback("agent", agent_roles[0], f"Agent 1/{len(agent_roles)} gestart")
            ScanJob.objects.filter(pk=job_pk).update(
                active_agent=agent_roles[0],
                progress_message=f"Agent 1/{len(agent_roles)}: {agent_roles[0]}",
            )

        import io
        import sys
        with _stdout_lock:
            original_stdout = sys.stdout
            try:
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
                )
            except AttributeError:
                pass
            try:
                result = crew.kickoff()
            finally:
                sys.stdout = original_stdout

        raw_output = str(result.raw) if hasattr(result, "raw") else str(result)

        # Archive the investigation result
        ComplianceReport.objects.create(
            report_type="investigation",
            entity_name=entity_name,
            job=job,
            summary=raw_output[:5000],
        )

        job.status = "completed"
        job.progress_message = "Persoonsonderzoek afgerond"
        job.active_agent = ""
        job.tasks_completed = len(agent_roles)
        job.finished_at = timezone.now()
        job.save()
        log_callback("result", "System", f"Onderzoek afgerond.\n{raw_output[:500]}")

    except Exception as e:
        logger.error("Compliance investigation failed (job=%s)", job_pk, exc_info=True)
        job.status = "failed"
        logger.exception("Job %s failed", job.pk)
        job.error_message = "Er is een fout opgetreden. Controleer de logs voor details."
        job.progress_message = "Onderzoek mislukt"
        job.finished_at = timezone.now()
        job.save()
        log_callback("error", "System", f"Onderzoek mislukt: {type(e).__name__}")
    finally:
        close_old_connections()


# ---------------------------------------------------------------------------
# Business Types management
# ---------------------------------------------------------------------------

def business_types_manage(request):
    types = BusinessType.objects.all()
    return render(request, "dashboard/sales/business_types.html", {"types": types})


@require_POST
def htmx_business_type_add(request):
    google_type = request.POST.get("google_type", "").strip()
    label = request.POST.get("label", "").strip()
    if google_type and label:
        BusinessType.objects.get_or_create(google_type=google_type, defaults={"label": label})
    types = BusinessType.objects.all()
    return render(request, "dashboard/sales/_business_type_list.html", {"types": types})


@require_POST
def htmx_business_type_delete(request, pk):
    BusinessType.objects.filter(pk=pk).delete()
    types = BusinessType.objects.all()
    return render(request, "dashboard/sales/_business_type_list.html", {"types": types})


# ===================================================================
# Email Tracking views (public, no login required)
# ===================================================================

from django.views.decorators.csrf import csrf_exempt
import base64


# 1x1 transparent GIF
_TRACKING_PIXEL = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)


@csrf_exempt
def track_open(request, token):
    """Record an email open event and return a 1x1 transparent GIF."""
    if ProspectResponse.objects.filter(tracking_token=token).exists():
        TrackingEvent.objects.create(token=token, event_type="open")
    response = HttpResponse(_TRACKING_PIXEL, content_type="image/gif")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@csrf_exempt
def track_click(request, token):
    """Record a click event and redirect to the original URL."""
    from urllib.parse import urlparse
    url = request.GET.get("url", "")
    redirect_url = "/"
    tracking_base = getattr(settings, "TRACKING_BASE_URL", "")
    # Only allow redirects when TRACKING_BASE_URL is explicitly configured
    if url and url.startswith(("http://", "https://")) and tracking_base:
        allowed_host = urlparse(tracking_base).hostname
        url_host = urlparse(url).hostname
        if (
            allowed_host
            and url_host
            and url_host.removeprefix("www.") == allowed_host.removeprefix("www.")
        ):
            redirect_url = url
    if ProspectResponse.objects.filter(tracking_token=token).exists():
        TrackingEvent.objects.create(token=token, event_type="click", url=redirect_url)
    return redirect(redirect_url)


# ═══════════════════════════════════════════════════════════════════
# VACANCY SCRAPING (within Sales module)
# ═══════════════════════════════════════════════════════════════════

def vacancy_search(request):
    """Vacancy search page — scrape job postings to find prospect companies."""
    groups = _user_groups(request)
    # Check which API sources are configured
    sources_status = {
        "jooble": bool(getattr(settings, "JOOBLE_API_KEY", "")),
        "adzuna": bool(
            getattr(settings, "ADZUNA_APP_ID", "")
            and getattr(settings, "ADZUNA_APP_KEY", "")
        ),
        "careerjet": bool(getattr(settings, "CAREERJET_AFFID", "")),
    }
    return render(request, "dashboard/sales/vacancy_search.html", {
        "groups": groups,
        "sources_status": sources_status,
        "categories": VacancyMonitorService.CATEGORIES,
        "locations": VacancyMonitorService.NOORD_NEDERLAND_LOCATIONS,
    })


def htmx_vacancy_results(request):
    """HTMX partial: search vacancies and return results grouped by company."""
    query = request.GET.get("query", "").strip()
    location = request.GET.get("location", "").strip()
    sources = request.GET.getlist("sources") or ["jooble", "adzuna", "careerjet"]
    group_slug = request.GET.get("group_slug", "").strip()

    if not query:
        return render(request, "dashboard/sales/_vacancy_results.html", {
            "error": "Voer een zoekterm in.",
        })

    service = VacancyMonitorService()
    vacancies = service.search_all(query, location=location, sources=sources)

    # Store vacancies in DB (dedup on external_id)
    stored_count = 0
    for v in vacancies:
        _, created = Vacancy.objects.get_or_create(
            external_id=v["external_id"],
            defaults={
                "title": v["title"][:500],
                "company_name": v["company_name"][:300],
                "location": v.get("location", "")[:300],
                "category": v.get("category", ""),
                "description": v.get("description", ""),
                "salary": v.get("salary", "")[:200],
                "source_url": v.get("source_url", "")[:500],
                "source": v["source"],
                "published_date": v.get("published_date"),
                "relevance_score": v.get("relevance_score", 0),
            },
        )
        if created:
            stored_count += 1

    # Group by company
    companies = service.extract_companies(vacancies)

    # Check dedup: mark companies that already exist as prospects
    new_company_count = 0
    for company in companies:
        match = find_existing_prospect(company["name"])
        company["existing_prospect"] = match
        company["already_saved"] = match is not None
        if not match:
            new_company_count += 1

    # Log search for structural tracking
    avg_rel = 0
    if vacancies:
        avg_rel = round(sum(v.get("relevance_score", 0) for v in vacancies) / len(vacancies))
    VacancySearch.objects.create(
        query=query,
        location=location,
        sources_used=", ".join(sources),
        results_count=len(vacancies),
        companies_found=len(companies),
        new_companies=new_company_count,
        avg_relevance=avg_rel,
    )

    # Category labels for display
    cat_labels = {k: v["label"] for k, v in VacancyMonitorService.CATEGORIES.items()}

    return render(request, "dashboard/sales/_vacancy_results.html", {
        "companies": companies,
        "total_vacancies": len(vacancies),
        "total_companies": len(companies),
        "new_stored": stored_count,
        "cat_labels": cat_labels,
        "group_slug": group_slug,
        "sources_used": ", ".join(s.capitalize() for s in sources),
    })


@require_POST
def htmx_vacancy_save_company(request):
    """Save a single company from vacancy results as a prospect."""
    company_name = request.POST.get("company_name", "").strip()
    location = request.POST.get("location", "").strip()
    group_slug = request.POST.get("group_slug", "").strip()

    if not company_name:
        return HttpResponse(
            '<span class="text-xs text-red-500">Naam ontbreekt</span>'
        )

    # Check dedup
    prospect = find_existing_prospect(company_name)

    if not prospect:
        # Try Google Places for enrichment
        enriched = {}
        try:
            places_service = GooglePlacesService()
            search_query = f"{company_name} {location}".strip()
            results = places_service.text_search(search_query, max_results=1)
            if results:
                enriched = results[0]
        except Exception:
            logger.debug("Google Places lookup failed for %s", company_name)

        # Create prospect
        prospect = Prospect(
            place_id=enriched.get("place_id", ""),
            name=company_name,
            address=enriched.get("address", ""),
            phone=enriched.get("phone", ""),
            website=enriched.get("website", ""),
            business_type=enriched.get("business_type", ""),
        )
        if enriched.get("rating"):
            try:
                prospect.google_rating = float(enriched["rating"])
            except (ValueError, TypeError):
                pass
        prospect.google_reviews_count = _safe_int(enriched.get("reviews_count"), 0)
        if enriched.get("latitude"):
            try:
                prospect.latitude = float(enriched["latitude"])
            except (ValueError, TypeError):
                pass
        if enriched.get("longitude"):
            try:
                prospect.longitude = float(enriched["longitude"])
            except (ValueError, TypeError):
                pass
        prospect.save()

        # Auto-scrape contact info
        if prospect.website and not prospect.email:
            try:
                info = scrape_contact_info(prospect.website)
                update_fields = []
                if info.email:
                    prospect.email = info.email
                    update_fields.append("email")
                if info.contact_first_name and not prospect.contact_first_name:
                    prospect.contact_first_name = info.contact_first_name
                    update_fields.append("contact_first_name")
                if info.contact_last_name and not prospect.contact_last_name:
                    prospect.contact_last_name = info.contact_last_name
                    update_fields.append("contact_last_name")
                if not prospect.aanhef:
                    prospect.aanhef = "Geachte heer/mevrouw"
                    update_fields.append("aanhef")
                if update_fields:
                    prospect.save(update_fields=update_fields)
            except Exception:
                logger.exception("Contact scrape failed for %s", prospect.website)

    # Add to group
    if group_slug:
        group = _user_groups(request).filter(slug=group_slug).first()
        if group:
            prospect.groups.add(group)

    # Link vacancies to this prospect
    Vacancy.objects.filter(
        company_name__iexact=company_name, prospect__isnull=True
    ).update(prospect=prospect)

    # Return saved badge
    extra_info = ""
    if prospect.email:
        extra_info += (
            f' <span class="text-gray-400">\u00b7</span> '
            f'<span class="text-indigo-600">{html_escape(prospect.email)}</span>'
        )
    if prospect.contact_first_name or prospect.contact_last_name:
        cname = f"{prospect.contact_first_name} {prospect.contact_last_name}".strip()
        extra_info += (
            f' <span class="text-gray-400">\u00b7</span> '
            f'<span class="text-gray-600">{html_escape(cname)}</span>'
        )
    return HttpResponse(
        f'<span class="inline-flex items-center gap-1 text-xs font-medium text-emerald-600">'
        f'<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
        f'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>'
        f'</svg> Opgeslagen{extra_info}</span>'
    )


@require_POST
def htmx_vacancy_save_all(request):
    """Bulk save all companies from vacancy results as prospects."""
    company_names_json = request.POST.get("company_names", "[]")
    locations_json = request.POST.get("locations", "{}")
    group_slug = request.POST.get("group_slug", "").strip()

    try:
        company_names = json.loads(company_names_json)
        locations_map = json.loads(locations_json)
    except (json.JSONDecodeError, TypeError):
        return _toast_response(HttpResponse(""), "error", "Ongeldige data.")

    if not isinstance(company_names, list):
        return _toast_response(HttpResponse(""), "error", "Ongeldige data.")

    group = _user_groups(request).filter(slug=group_slug).first() if group_slug else None
    saved_count = 0
    skipped_count = 0

    for name in company_names:
        name = name.strip()
        if not name:
            continue

        # Check dedup
        prospect = find_existing_prospect(name)
        if prospect:
            # Still add to group if not already there
            if group and not prospect.groups.filter(pk=group.pk).exists():
                prospect.groups.add(group)
            skipped_count += 1
            continue

        location = locations_map.get(name, "")

        # Try Google Places enrichment
        enriched = {}
        try:
            places_service = GooglePlacesService()
            search_query = f"{name} {location}".strip()
            results = places_service.text_search(search_query, max_results=1)
            if results:
                enriched = results[0]
        except Exception:
            logger.debug("Google Places lookup failed for %s", name)

        prospect = Prospect(
            place_id=enriched.get("place_id", ""),
            name=name,
            address=enriched.get("address", ""),
            phone=enriched.get("phone", ""),
            website=enriched.get("website", ""),
            business_type=enriched.get("business_type", ""),
        )
        if enriched.get("rating"):
            try:
                prospect.google_rating = float(enriched["rating"])
            except (ValueError, TypeError):
                pass
        prospect.google_reviews_count = _safe_int(enriched.get("reviews_count"), 0)
        prospect.save()

        # Auto-scrape contact info
        if prospect.website and not prospect.email:
            try:
                info = scrape_contact_info(prospect.website)
                update_fields = []
                if info.email:
                    prospect.email = info.email
                    update_fields.append("email")
                if info.contact_first_name:
                    prospect.contact_first_name = info.contact_first_name
                    update_fields.append("contact_first_name")
                if info.contact_last_name:
                    prospect.contact_last_name = info.contact_last_name
                    update_fields.append("contact_last_name")
                if not prospect.aanhef:
                    prospect.aanhef = "Geachte heer/mevrouw"
                    update_fields.append("aanhef")
                if update_fields:
                    prospect.save(update_fields=update_fields)
            except Exception:
                logger.exception("Contact scrape failed for %s", prospect.website)

        if group:
            prospect.groups.add(group)

        # Link vacancies
        Vacancy.objects.filter(
            company_name__iexact=name, prospect__isnull=True
        ).update(prospect=prospect)

        saved_count += 1

    msg = f"{saved_count} bedrijven opgeslagen als prospects"
    if skipped_count:
        msg += f" ({skipped_count} al bestaand)"
    return _toast_response(HttpResponse(""), "success", msg)


def vacancy_analysis(request):
    """Vacancy analysis dashboard — trends, top companies, search history."""
    from datetime import timedelta

    now = timezone.now()
    week_ago = now - timedelta(days=7)

    # KPIs
    total_vacancies = Vacancy.objects.count()
    total_companies = Vacancy.objects.values("company_name").distinct().count()
    new_this_week = Vacancy.objects.filter(created_at__gte=week_ago).count()
    avg_relevance = Vacancy.objects.aggregate(
        avg=db_models.Avg("relevance_score")
    )["avg"] or 0
    high_relevance = Vacancy.objects.filter(relevance_score__gte=50).count()

    # Top companies by relevance (from DB)
    top_companies = (
        Vacancy.objects.values("company_name")
        .annotate(
            vacancy_count=Count("id"),
            max_relevance=db_models.Max("relevance_score"),
            avg_relevance=db_models.Avg("relevance_score"),
        )
        .filter(vacancy_count__gte=1)
        .order_by("-max_relevance", "-vacancy_count")[:20]
    )

    # Check which are already prospects
    for c in top_companies:
        match = find_existing_prospect(c["company_name"])
        c["is_prospect"] = match is not None
        c["prospect"] = match

    # Category distribution
    categories = (
        Vacancy.objects.exclude(category="")
        .values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    cat_labels = {k: v["label"] for k, v in VacancyMonitorService.CATEGORIES.items()}

    # Relevance distribution
    relevance_ranges = {
        "0-25": Vacancy.objects.filter(relevance_score__lt=25).count(),
        "25-50": Vacancy.objects.filter(relevance_score__gte=25, relevance_score__lt=50).count(),
        "50-75": Vacancy.objects.filter(relevance_score__gte=50, relevance_score__lt=75).count(),
        "75-100": Vacancy.objects.filter(relevance_score__gte=75).count(),
    }

    # Search history
    recent_searches = VacancySearch.objects.all()[:10]

    return render(request, "dashboard/sales/vacancy_analysis.html", {
        "total_vacancies": total_vacancies,
        "total_companies": total_companies,
        "new_this_week": new_this_week,
        "avg_relevance": round(avg_relevance),
        "high_relevance": high_relevance,
        "top_companies": top_companies,
        "categories": categories,
        "cat_labels": cat_labels,
        "relevance_ranges": relevance_ranges,
        "recent_searches": recent_searches,
    })
