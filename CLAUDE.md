# FenoFin Monitor

## Wat is dit?
Agentic dependency monitor + fiscale bedrijfsmonitor met dynamische AI Team Builder.
Django 6 + CrewAI + HTMX + Tailwind CSS + Tom Select.

## Projectstructuur
- `config/` — Django settings, root urls, wsgi
- `dashboard/` — Hoofd-app: models, views, urls, templates, admin
- `monitor/` — Dependency monitoring crew + tools + YAML config
- `fiscal/` — Fiscale monitoring crew + tools + YAML config

## Belangrijke bestanden
- `dashboard/models.py` — Alle models (Team, TeamAgent, TeamTask, TeamVariable, ScanJob, Report, Finding, BlogArticle)
- `dashboard/views.py` — Alle views inclusief team builder CRUD en background runners
- `dashboard/urls.py` — URL patterns (50 routes)
- `dashboard/crew_builder.py` — Dynamisch crews bouwen vanuit DB teams
- `dashboard/tool_registry.py` — Registry van 13 tools
- `monitor/crew.py` — Hardcoded dependency monitor crew (fallback)
- `fiscal/crew.py` — Hardcoded fiscal crew (fallback)

## Architectuur
- Background threads voor CrewAI runs (geen Celery)
- HTMX voor partial page updates (polling elke 5s tijdens runs)
- Team Builder: teams/agents/taken/variabelen volledig configureerbaar via UI
- 3 LLM providers: Gemini, Anthropic, OpenAI (per agent instelbaar)
- Variable interpolatie: `{var_name}` in agent goals en task descriptions

## Conventies
- Templates: Tailwind CSS via CDN, Inter font, indigo/purple kleurenpalet
- Nederlandse UI-teksten, Engelse code
- HTMX partials in `_naam.html`, full pages zonder underscore
- Views retourneren partials bij `request.htmx`, full page anders
- **Alle `<select>` elementen gebruiken Tom Select** (CDN via base.html)
  - Globale init via `initTomSelects()` in base.html — pakt automatisch alle `<select>` op
  - HTMX lifecycle: destroy voor swap (`htmx:beforeSwap`), re-init na swap (`htmx:afterSettle`)
  - Custom indigo theme in base.html `<style>` blok (`.ts-wrapper`, `.ts-dropdown`, etc.)
  - Nieuwe selects hoeven geen extra attributen — worden automatisch geïnitialiseerd
- **Toast notificaties** — 3 entry points:
  - Django `messages` framework → automatisch gerenderd als toasts bij page load
  - `HX-Trigger: showToast` header → voor HTMX responses, via `_toast_response()` helper in views.py
  - `showToast({type, message, duration})` JS API → voor client-side gebruik
- **Modal bevestigingsdialogen** — vervangt alle browser `confirm()` dialogen:
  - `hx-confirm` attributen worden automatisch geïntercepteerd (geen template wijzigingen nodig)
  - `data-confirm` attribuut op `<form>` elementen voor non-HTMX forms
  - `showModal({title, message, onConfirm, variant})` JS API → voor programmatisch gebruik
- **View conventie**: `_toast_response(response, type, message)` voor HTMX views, `messages.success(request, msg)` voor redirect views

## Commando's
- `python manage.py runserver` — Start dev server
- `python manage.py makemigrations && python manage.py migrate` — Migraties
- `python manage.py shell` — Django shell

## Environment variabelen (.env)
- `GEMINI_API_KEY` — Gemini API key
- `ANTHROPIC_API_KEY` — Anthropic API key (optioneel)
- `OPENAI_API_KEY` — OpenAI API key (optioneel)
- `MONITORED_PROJECT_PATH` — Pad naar het te monitoren project
- `SMTP_HOST/PORT/USER/PASSWORD` — E-mail configuratie
