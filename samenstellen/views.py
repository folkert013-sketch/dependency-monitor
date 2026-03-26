import io
import json
import logging
import sys
import threading
import uuid as _uuid
from pathlib import Path as _Path

from django.conf import settings
from django.contrib import messages
from django.db import close_old_connections
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from dashboard.models import ScanJob, ScanLog, Team

from .models import Document, Fase, FaseResultaat, Opdracht

logger = logging.getLogger(__name__)

# Re-use the shared executor and stdout lock from dashboard
from dashboard.views import _scan_executor, _stdout_lock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _toast_response(response, toast_type, message):
    response["HX-Trigger"] = json.dumps(
        {"showToast": {"type": toast_type, "message": message}}
    )
    return response


def _home_context():
    """Build context for the home page."""
    fasen = Fase.objects.select_related("team").all()
    opdrachten = Opdracht.objects.all()[:20]
    teams = Team.objects.all()
    return {
        "fasen": fasen,
        "opdrachten": opdrachten,
        "teams": teams,
    }


def _opdracht_context(opdracht):
    """Build context for the detail page."""
    fasen = Fase.objects.select_related("team").all()
    fase_resultaten = {
        fr.fase_id: fr
        for fr in opdracht.fase_resultaten.select_related("fase").all()
    }
    documenten_per_fase = {}
    for doc in opdracht.documenten.select_related("fase").all():
        key = doc.fase_id or "algemeen"
        documenten_per_fase.setdefault(key, []).append(doc)

    # Determine active job
    active_job = None
    active_job_logs = []
    if opdracht.status == "run1_bezig" and opdracht.run1_job:
        active_job = opdracht.run1_job
    elif opdracht.status == "run2_bezig" and opdracht.run2_job:
        active_job = opdracht.run2_job

    if active_job:
        active_job.refresh_from_db()
        active_job_logs = active_job.logs.all()

    # Build phase states
    fasen_met_status = []
    for fase in fasen:
        fr = fase_resultaten.get(fase.pk)
        fase_status = fr.status if fr else "idle"
        fasen_met_status.append({
            "fase": fase,
            "resultaat": fr,
            "status": fase_status,
            "documenten": documenten_per_fase.get(fase.pk, []),
        })

    return {
        "opdracht": opdracht,
        "fasen_met_status": fasen_met_status,
        "active_job": active_job,
        "active_job_logs": active_job_logs,
        "documenten_algemeen": documenten_per_fase.get("algemeen", []),
        "teams": Team.objects.all(),
    }


# ---------------------------------------------------------------------------
# Home — overzicht + faseconfiguratie
# ---------------------------------------------------------------------------

def home(request):
    return render(request, "samenstellen/home.html", _home_context())


# ---------------------------------------------------------------------------
# Fase configuratie
# ---------------------------------------------------------------------------

@require_POST
def fase_edit(request, pk):
    """Edit fase doelen, randvoorwaarden, referenties."""
    fase = get_object_or_404(Fase, pk=pk)
    fase.beschrijving = request.POST.get("beschrijving", fase.beschrijving)
    fase.doelen = request.POST.get("doelen", fase.doelen)
    fase.randvoorwaarden = request.POST.get("randvoorwaarden", fase.randvoorwaarden)
    fase.referenties = request.POST.get("referenties", fase.referenties)
    fase.save()
    response = render(request, "samenstellen/_fase_card.html", {
        "fase": fase, "teams": Team.objects.all(),
    })
    return _toast_response(response, "success", f"Fase '{fase.naam}' bijgewerkt")


@require_POST
def fase_koppel(request, pk):
    """Koppel een AI Team aan een fase."""
    fase = get_object_or_404(Fase, pk=pk)
    team_id = request.POST.get("team_id")
    if team_id:
        fase.team = get_object_or_404(Team, pk=team_id)
    else:
        fase.team = None
    fase.save()
    response = render(request, "samenstellen/_fase_card.html", {
        "fase": fase, "teams": Team.objects.all(),
    })
    return _toast_response(response, "success", f"Team gekoppeld aan '{fase.naam}'")


# ---------------------------------------------------------------------------
# Opdracht CRUD
# ---------------------------------------------------------------------------

@require_POST
def opdracht_create(request):
    """Maak een nieuwe samenstelopdracht aan."""
    opdracht = Opdracht.objects.create(
        client_naam=request.POST.get("client_naam", "").strip(),
        boekjaar=request.POST.get("boekjaar", "2025").strip(),
        rechtsvorm=request.POST.get("rechtsvorm", "BV").strip(),
        sector=request.POST.get("sector", "").strip(),
        verslaggevingsstelsel=request.POST.get("verslaggevingsstelsel", "RJ").strip(),
    )

    # Handle concept PDF upload
    uploaded = request.FILES.get("concept_pdf")
    if uploaded and uploaded.name.lower().endswith(".pdf"):
        opdracht.ensure_dossier_dirs()
        safe_name = f"{_uuid.uuid4().hex[:8]}_{uploaded.name}"
        file_path = opdracht.dossier_path / safe_name
        with open(file_path, "wb") as f:
            for chunk in uploaded.chunks():
                f.write(chunk)
        opdracht.concept_pdf = str(file_path)
        opdracht.save(update_fields=["concept_pdf"])

    messages.success(request, f"Samenstelopdracht voor {opdracht.client_naam} aangemaakt")
    return redirect("samenstellen:opdracht_detail", pk=opdracht.pk)


def opdracht_detail(request, pk):
    """Detail/workflow pagina voor een samenstelopdracht."""
    opdracht = get_object_or_404(Opdracht, pk=pk)
    return render(request, "samenstellen/detail.html", _opdracht_context(opdracht))


@require_POST
def opdracht_delete(request, pk):
    """Verwijder een samenstelopdracht."""
    opdracht = get_object_or_404(Opdracht, pk=pk)
    naam = opdracht.client_naam
    opdracht.delete()
    messages.success(request, f"Samenstelopdracht voor {naam} verwijderd")
    return redirect("samenstellen:home")


# ---------------------------------------------------------------------------
# Uitvoering — run, status, stop
# ---------------------------------------------------------------------------

@require_POST
def opdracht_run(request, pk, run_nr):
    """Start run 1 of run 2 van de samenstelopdracht."""
    opdracht = get_object_or_404(Opdracht, pk=pk)

    # Check of er al een actieve run is
    if opdracht.status in ("run1_bezig", "run2_bezig"):
        ctx = _opdracht_context(opdracht)
        return render(request, "samenstellen/_status.html", ctx)

    # Check of fasen geconfigureerd zijn
    fasen = Fase.objects.filter(run_nummer=run_nr, team__isnull=False)
    if not fasen.exists():
        response = render(request, "samenstellen/_status.html", _opdracht_context(opdracht))
        return _toast_response(response, "error", "Koppel eerst teams aan alle fasen")

    # Maak ScanJob aan
    job = ScanJob.objects.create(
        status="pending",
        job_type="samenstelopdracht",
        run_variables={
            "client_naam": opdracht.client_naam,
            "boekjaar": opdracht.boekjaar,
            "run_nummer": run_nr,
        },
        progress_message=f"Samenstelopdracht run {run_nr} wordt gestart...",
    )

    if run_nr == 1:
        opdracht.run1_job = job
        opdracht.status = "run1_bezig"
    else:
        opdracht.run2_job = job
        opdracht.status = "run2_bezig"
    opdracht.save()

    # Ensure dossier dirs exist
    opdracht.ensure_dossier_dirs()

    # Submit to background
    _scan_executor.submit(
        _run_samenstelopdracht_background, job.pk, opdracht.pk, run_nr,
    )

    ctx = _opdracht_context(opdracht)
    ctx["active_job"] = job
    ctx["active_job_logs"] = []
    return render(request, "samenstellen/_status.html", ctx)


def opdracht_status(request, pk):
    """HTMX polling endpoint voor samenstelopdracht voortgang."""
    opdracht = get_object_or_404(Opdracht, pk=pk)
    ctx = _opdracht_context(opdracht)

    # Check staleness
    if ctx["active_job"] and ctx["active_job"].status == "running":
        last_log = ctx["active_job"].logs.order_by("-created_at").first()
        if last_log:
            seconds = int((timezone.now() - last_log.created_at).total_seconds())
            if seconds > 900:
                ctx["stale"] = True
                ctx["last_activity_seconds"] = seconds

    return render(request, "samenstellen/_status.html", ctx)


@require_POST
def opdracht_stop(request, pk):
    """Stop een actieve samenstelopdracht run."""
    opdracht = get_object_or_404(Opdracht, pk=pk)

    active_job = None
    if opdracht.status == "run1_bezig" and opdracht.run1_job:
        active_job = opdracht.run1_job
        opdracht.status = "nieuw"
    elif opdracht.status == "run2_bezig" and opdracht.run2_job:
        active_job = opdracht.run2_job
        opdracht.status = "run1_klaar"

    if active_job and active_job.status in ("pending", "running"):
        active_job.status = "failed"
        active_job.progress_message = "Run handmatig gestopt"
        active_job.finished_at = timezone.now()
        active_job.save()
        ScanLog.objects.create(
            job=active_job, event_type="error", agent_name="System",
            message="Samenstelopdracht run gestopt door gebruiker",
        )

    opdracht.save()
    ctx = _opdracht_context(opdracht)
    response = render(request, "samenstellen/_status.html", ctx)
    return _toast_response(response, "warning", "Run gestopt")


# ---------------------------------------------------------------------------
# Upload definitieve versie
# ---------------------------------------------------------------------------

@require_POST
def upload_definitief(request, pk):
    """Upload de definitieve jaarrekening na correcties."""
    opdracht = get_object_or_404(Opdracht, pk=pk)

    uploaded = request.FILES.get("definitieve_pdf")
    if not uploaded or not uploaded.name.lower().endswith(".pdf"):
        response = render(request, "samenstellen/_status.html", _opdracht_context(opdracht))
        return _toast_response(response, "error", "Upload een geldig PDF-bestand")

    opdracht.ensure_dossier_dirs()
    safe_name = f"definitief_{_uuid.uuid4().hex[:8]}_{uploaded.name}"
    file_path = opdracht.dossier_path / safe_name
    with open(file_path, "wb") as f:
        for chunk in uploaded.chunks():
            f.write(chunk)

    opdracht.definitieve_pdf = str(file_path)
    opdracht.save(update_fields=["definitieve_pdf"])

    ctx = _opdracht_context(opdracht)
    response = render(request, "samenstellen/_status.html", ctx)
    return _toast_response(response, "success", "Definitieve jaarrekening geupload")


# ---------------------------------------------------------------------------
# Documenten
# ---------------------------------------------------------------------------

@require_POST
def document_upload(request, pk):
    """Upload een document en koppel aan een fase."""
    opdracht = get_object_or_404(Opdracht, pk=pk)
    uploaded = request.FILES.get("document")
    fase_id = request.POST.get("fase_id")

    if not uploaded:
        response = render(request, "samenstellen/_documenten.html", _opdracht_context(opdracht))
        return _toast_response(response, "error", "Selecteer een bestand")

    fase = None
    subfolder = "algemeen"
    if fase_id:
        fase = get_object_or_404(Fase, pk=fase_id)
        subfolder = fase.fase_key

    opdracht.ensure_dossier_dirs()
    doc_dir = opdracht.dossier_path / subfolder
    doc_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{_uuid.uuid4().hex[:8]}_{uploaded.name}"
    file_path = doc_dir / safe_name
    with open(file_path, "wb") as f:
        for chunk in uploaded.chunks():
            f.write(chunk)

    Document.objects.create(
        opdracht=opdracht,
        fase=fase,
        naam=uploaded.name,
        bestand=str(file_path),
    )

    ctx = _opdracht_context(opdracht)
    response = render(request, "samenstellen/_documenten.html", ctx)
    return _toast_response(response, "success", f"Document '{uploaded.name}' toegevoegd")


@require_POST
def document_delete(request, pk, doc_pk):
    """Verwijder een document."""
    opdracht = get_object_or_404(Opdracht, pk=pk)
    doc = get_object_or_404(Document, pk=doc_pk, opdracht=opdracht)
    naam = doc.naam

    # Delete file from disk
    try:
        _Path(doc.bestand).unlink(missing_ok=True)
    except Exception:
        pass

    doc.delete()
    ctx = _opdracht_context(opdracht)
    response = render(request, "samenstellen/_documenten.html", ctx)
    return _toast_response(response, "success", f"Document '{naam}' verwijderd")


# ---------------------------------------------------------------------------
# Background orchestrator
# ---------------------------------------------------------------------------

def _run_samenstelopdracht_background(job_pk: int, opdracht_pk: int, run_nummer: int):
    """Run meerdere teams sequentieel per fase van de samenstelopdracht."""
    try:
        import django
        django.setup()
    except Exception:
        logger.error("django.setup() failed in _run_samenstelopdracht_background", exc_info=True)
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dashboard_scanjob SET status='failed', "
                    "error_message='Django setup failed' WHERE id=%s",
                    [job_pk],
                )
        except Exception:
            pass
        return

    close_old_connections()
    from dashboard.crew_builder import build_crew_from_team

    job = ScanJob.objects.get(pk=job_pk)
    job.status = "running"
    job.progress_message = f"Samenstelopdracht run {run_nummer} gestart..."
    job.save(update_fields=["status", "progress_message"])

    opdracht = Opdracht.objects.get(pk=opdracht_pk)

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
            logger.error("Error in samenstelopdracht log_callback", exc_info=True)

    try:
        fasen = list(
            Fase.objects.filter(run_nummer=run_nummer, team__isnull=False)
            .select_related("team")
            .order_by("order")
        )

        if not fasen:
            raise ValueError(f"Geen fasen met teams geconfigureerd voor run {run_nummer}")

        log_callback("start", "System", f"Samenstelopdracht run {run_nummer} — {len(fasen)} fasen")

        # Base variables from the opdracht
        base_vars = {
            "client_naam": opdracht.client_naam,
            "boekjaar": opdracht.boekjaar,
            "rechtsvorm": opdracht.rechtsvorm,
            "sector": opdracht.sector,
            "verslaggevingsstelsel": opdracht.verslaggevingsstelsel,
            "jaarrekening_path": (
                opdracht.concept_pdf if run_nummer == 1 else opdracht.definitieve_pdf
            ),
        }

        total_fasen = len(fasen)
        vorig_resultaat = ""

        for i, fase in enumerate(fasen):
            if _is_cancelled():
                break

            # Create or update fase resultaat
            fase_res, _ = FaseResultaat.objects.update_or_create(
                opdracht=opdracht,
                fase=fase,
                defaults={
                    "status": "running",
                    "started_at": timezone.now(),
                    "resultaat": "",
                },
            )

            log_callback(
                "agent",
                fase.naam,
                f"Fase {i + 1}/{total_fasen}: {fase.naam} gestart",
            )
            ScanJob.objects.filter(pk=job_pk).update(
                active_agent=fase.naam,
                progress_message=f"Fase {i + 1}/{total_fasen}: {fase.naam}",
            )

            # Build run variables: base + fase context + previous result
            run_vars = {
                **base_vars,
                "fase_doelen": fase.doelen,
                "fase_randvoorwaarden": fase.randvoorwaarden,
                "fase_referenties": fase.referenties,
                "vorig_fase_resultaat": vorig_resultaat,
            }

            # Merge team-specific variable defaults
            for var in fase.team.variables.all():
                if var.name not in run_vars:
                    run_vars[var.name] = var.default_value

            # Build crew callbacks
            task_lock = threading.Lock()
            agent_roles = list(
                fase.team.agents.order_by("order").values_list("role", flat=True)
            )
            task_index = [0]

            def make_step_cb(fase_naam, roles):
                def step_cb(step_output):
                    try:
                        tool = getattr(step_output, "tool", "")
                        thought = getattr(step_output, "thought", "") or getattr(step_output, "log", "")
                        output = getattr(step_output, "output", "")
                        with task_lock:
                            idx = min(task_index[0], len(roles) - 1) if roles else 0
                        agent_name = roles[idx] if idx < len(roles) else fase_naam

                        if tool:
                            log_callback("tool", agent_name, f"Tool: {tool}")
                        elif thought and not output:
                            log_callback("thought", agent_name, str(thought)[:300])
                        elif output:
                            log_callback("result", agent_name, str(output)[:400])
                    except Exception:
                        logger.error("Error in samenstelopdracht step_cb", exc_info=True)
                return step_cb

            def make_task_cb(roles):
                def task_cb(task_output):
                    try:
                        with task_lock:
                            idx = task_index[0]
                            task_index[0] = idx + 1
                        agent_name = roles[idx] if idx < len(roles) else "Agent"
                        summary = str(getattr(task_output, "raw", ""))[:300]
                        log_callback("task_done", agent_name, f"Taak afgerond\n{summary}")
                    except Exception:
                        logger.error("Error in samenstelopdracht task_cb", exc_info=True)
                return task_cb

            step_cb = make_step_cb(fase.naam, agent_roles)
            task_cb = make_task_cb(agent_roles)

            # Build and run crew
            crew, agents_list = build_crew_from_team(
                fase.team, run_vars,
                step_callback=step_cb, task_callback=task_cb,
            )

            if agent_roles:
                log_callback("agent", agent_roles[0], f"{agent_roles[0]} gestart")

            with _stdout_lock:
                original_stdout = sys.stdout
                try:
                    sys.stdout = io.TextIOWrapper(
                        sys.stdout.buffer, encoding="utf-8", errors="replace",
                        line_buffering=True,
                    )
                except AttributeError:
                    pass
                try:
                    result = crew.kickoff()
                finally:
                    sys.stdout = original_stdout

            raw_output = str(result.raw) if hasattr(result, "raw") else str(result)
            vorig_resultaat = raw_output

            # Extract tokens
            total_tokens = 0
            if hasattr(result, "token_usage"):
                usage = result.token_usage
                total_tokens = getattr(usage, "total_tokens", 0) or 0

            # Save fase result to DB
            fase_res.status = "completed"
            fase_res.resultaat = raw_output
            fase_res.completed_at = timezone.now()
            fase_res.token_count = total_tokens
            fase_res.save()

            # Save result to dossier folder
            try:
                dossier_dir = opdracht.dossier_path / fase.fase_key
                dossier_dir.mkdir(parents=True, exist_ok=True)
                (dossier_dir / "resultaat.md").write_text(raw_output, encoding="utf-8")
            except Exception:
                logger.warning("Could not write fase result to dossier", exc_info=True)

            log_callback(
                "task_done",
                fase.naam,
                f"Fase {i + 1}/{total_fasen}: {fase.naam} afgerond",
            )

            # Update job progress
            ScanJob.objects.filter(pk=job_pk).update(
                tasks_completed=i + 1,
                progress_message=f"Fase {i + 1}/{total_fasen} afgerond: {fase.naam}",
            )

        # All phases complete
        job.refresh_from_db()
        job.status = "completed"
        job.progress_message = f"Run {run_nummer} afgerond — {total_fasen} fasen voltooid"
        job.active_agent = ""
        job.tasks_completed = total_fasen
        job.finished_at = timezone.now()
        job.save()

        opdracht.refresh_from_db()
        opdracht.status = "run1_klaar" if run_nummer == 1 else "afgerond"
        opdracht.save(update_fields=["status"])

        log_callback("result", "System", f"Samenstelopdracht run {run_nummer} afgerond")

    except Exception as e:
        logger.error(
            "Samenstelopdracht run failed (job=%s, opdracht=%s)",
            job_pk, opdracht_pk, exc_info=True,
        )
        job.refresh_from_db()
        job.status = "failed"
        job.error_message = "Er is een fout opgetreden. Controleer de logs voor details."
        job.progress_message = "Run mislukt"
        job.finished_at = timezone.now()
        job.save()

        # Mark any running fase as failed
        FaseResultaat.objects.filter(
            opdracht_id=opdracht_pk, status="running",
        ).update(status="failed", completed_at=timezone.now())

        # Reset opdracht status
        try:
            opdracht.refresh_from_db()
            if opdracht.status == "run1_bezig":
                opdracht.status = "nieuw"
            elif opdracht.status == "run2_bezig":
                opdracht.status = "run1_klaar"
            opdracht.save(update_fields=["status"])
        except Exception:
            pass

        log_callback("error", "System", f"Run mislukt: {e}")
    finally:
        close_old_connections()
