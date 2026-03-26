import re
import uuid

from django.conf import settings as django_settings
from django.db import IntegrityError, models
from django.db.models import Sum
from django.utils import timezone
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Team Builder models
# ---------------------------------------------------------------------------

def _save_with_unique_slug(instance, slug_field_max=190, slug_source_attr="name"):
    """Save a model with a unique slug, retrying on IntegrityError (K5)."""
    if not instance.slug:
        source = getattr(instance, slug_source_attr, "")
        instance.slug = slugify(source[:slug_field_max])
    original_slug = instance.slug
    for attempt in range(20):
        try:
            instance.save_base()
            return
        except IntegrityError:
            counter = attempt + 1
            instance.slug = f"{original_slug[:slug_field_max - 10]}-{counter}"
    # Exhausted retries — let the final attempt raise naturally
    instance.save_base()


class Team(models.Model):
    PROCESS_CHOICES = [
        ("sequential", "Sequential"),
        ("hierarchical", "Hierarchical"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, default="")
    process = models.CharField(max_length=15, choices=PROCESS_CHOICES, default="sequential")
    verbose = models.BooleanField(default=True)
    owner = models.ForeignKey(
        django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="teams", null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            _save_with_unique_slug(self, slug_field_max=190, slug_source_attr="name")
            return
        super().save(*args, **kwargs)


class TeamVariable(models.Model):
    INPUT_TYPE_CHOICES = [
        ("text", "Text"),
        ("textarea", "Textarea"),
        ("file_path", "File path"),
        ("select", "Select"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="variables")
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    input_type = models.CharField(max_length=10, choices=INPUT_TYPE_CHOICES, default="text")
    default_value = models.TextField(blank=True, default="")
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="Keuze-opties voor select type: [{value, label, tools?}]",
    )
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["team", "name"], name="unique_team_variable_name"),
        ]

    def __str__(self):
        return f"{self.team.name} — {self.name}"


class TeamAgent(models.Model):
    PROVIDER_CHOICES = [
        ("gemini", "Gemini"),
        ("anthropic", "Anthropic"),
        ("openai", "OpenAI"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="agents")
    order = models.PositiveIntegerField(default=0)
    role = models.CharField(max_length=200)
    goal = models.TextField()
    backstory = models.TextField(blank=True, default="")
    llm_provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="gemini")
    llm_model = models.CharField(max_length=100, default="gemini-3-flash-preview")
    tools = models.JSONField(default=list, blank=True)
    max_iter = models.PositiveIntegerField(default=25)
    verbose = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def clean(self):
        if self.is_manager and self.tools:
            self.tools = []

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.team.name} — {self.role}"


class TeamTask(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tasks")
    order = models.PositiveIntegerField(default=0)
    description = models.TextField()
    expected_output = models.TextField(blank=True, default="")
    agent = models.ForeignKey(TeamAgent, on_delete=models.CASCADE, related_name="tasks")
    context_tasks = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="downstream_tasks")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.team.name} — Taak {self.order}"


class ScanLog(models.Model):
    """Individual log entry produced during a scan."""
    EVENT_CHOICES = [
        ("start", "Start"),
        ("agent", "Agent actief"),
        ("tool", "Tool aangeroepen"),
        ("thought", "Agent denkt"),
        ("task_done", "Taak afgerond"),
        ("result", "Resultaat"),
        ("error", "Fout"),
        ("info", "Info"),
    ]

    job = models.ForeignKey("ScanJob", on_delete=models.CASCADE, related_name="logs")
    created_at = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=15, choices=EVENT_CHOICES, default="info")
    agent_name = models.CharField(max_length=100, blank=True, default="")
    message = models.TextField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.event_type}] {self.agent_name}: {self.message[:80]}"


class ScanJob(models.Model):
    """Tracks a running or completed scan."""
    STATUS_CHOICES = [
        ("pending", "Wachten"),
        ("running", "Bezig..."),
        ("completed", "Afgerond"),
        ("failed", "Mislukt"),
    ]
    JOB_TYPE_CHOICES = [
        ("dependency", "Dependency Monitor"),
        ("fiscal", "Bedrijfsmonitor"),
        ("custom", "Custom Team"),
        ("compliance", "WWFT Compliance"),
        ("vacancy", "Vacature Monitor"),
        ("samenstelopdracht", "Samenstelopdracht NV COS 4410"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default="dependency")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")
    run_variables = models.JSONField(default=dict, blank=True)
    progress_message = models.CharField(max_length=300, default="Scan starten...")
    active_agent = models.CharField(max_length=100, blank=True, default="")
    tasks_completed = models.IntegerField(default=0)
    token_count = models.IntegerField(default=0)
    report = models.ForeignKey("Report", on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    finished_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]


class TaskOutput(models.Model):
    """Stores the full output of each task in a crew run."""
    job = models.ForeignKey(ScanJob, on_delete=models.CASCADE, related_name="task_outputs")
    task_order = models.PositiveIntegerField()
    agent_name = models.CharField(max_length=200)
    task_description = models.TextField(blank=True, default="")
    output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["task_order"]

    def __str__(self):
        return f"[{self.task_order}] {self.agent_name}"


class Report(models.Model):
    STATUS_CHOICES = [
        ("critical", "Kritiek"),
        ("warning", "Waarschuwing"),
        ("ok", "Alles OK"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ok")
    total_dependencies = models.IntegerField(default=0)
    outdated_count = models.IntegerField(default=0)
    vulnerability_count = models.IntegerField(default=0)
    action_required = models.BooleanField(default=False)
    tip_of_the_week = models.TextField(blank=True, default="")
    quote_of_the_week = models.TextField(blank=True, default="")
    total_tokens = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    raw_output = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report {self.created_at:%Y-%m-%d %H:%M} — {self.get_status_display()}"

    @property
    def critical_findings(self):
        return self.findings.filter(severity="critical")

    @property
    def warning_findings(self):
        return self.findings.filter(severity="warning")

    @property
    def info_findings(self):
        return self.findings.filter(severity="info")


class Finding(models.Model):
    SEVERITY_CHOICES = [
        ("critical", "Kritiek"),
        ("warning", "Waarschuwing"),
        ("info", "Informatie"),
    ]
    CATEGORY_CHOICES = [
        ("security", "Security Vulnerability"),
        ("api_deprecation", "API Deprecation"),
        ("breaking_change", "Breaking Change"),
        ("outdated", "Verouderd Package"),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="findings")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, db_index=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)
    package_name = models.CharField(max_length=200)
    current_version = models.CharField(max_length=50, blank=True, default="")
    latest_version = models.CharField(max_length=50, blank=True, default="")
    summary = models.TextField()
    action_steps = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["severity", "package_name"]

    def __str__(self):
        return f"[{self.severity}] {self.package_name}: {self.summary[:60]}"


class BlogArticle(models.Model):
    """AI-generated fiscal blog article."""
    CATEGORY_CHOICES = [
        ("btw", "BTW"),
        ("ib", "Inkomstenbelasting"),
        ("vpb", "Vennootschapsbelasting"),
        ("loonbelasting", "Loonbelasting"),
        ("subsidies", "Subsidies"),
        ("deadlines", "Deadlines"),
        ("algemeen", "Algemeen"),
    ]
    STATUS_CHOICES = [
        ("draft", "Concept"),
        ("published", "Gepubliceerd"),
        ("archived", "Gearchiveerd"),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    intro = models.TextField(help_text="Korte, pakkende samenvatting (2-3 zinnen)")
    body = models.TextField(help_text="Artikel inhoud in markdown")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="algemeen")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft", db_index=True)
    sources = models.JSONField(default=list, blank=True, help_text="Bron-URLs")
    quality_score = models.PositiveSmallIntegerField(default=5, help_text="Kwaliteitsscore 1-10 van reviewer-agent")
    key_takeaways = models.JSONField(default=list, blank=True, help_text="Kernpunten van het artikel")
    action_items = models.JSONField(default=list, blank=True, help_text="Concrete actiepunten voor de ondernemer")
    deadline_date = models.DateField(null=True, blank=True, help_text="Relevante deadline datum")
    relevance_tags = models.JSONField(default=list, blank=True, help_text="Doelgroep tags (mkb, zzp, bv, etc.)")
    scan_job = models.ForeignKey(ScanJob, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_tokens = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quality_score__gte=1, quality_score__lte=10),
                name="quality_score_range",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title[:80]}"

    def save(self, *args, **kwargs):
        if not self.slug:
            _save_with_unique_slug(self, slug_field_max=290, slug_source_attr="title")
            return
        super().save(*args, **kwargs)


class ComplianceSection(models.Model):
    """A section of the WWFT compliance page, optionally updated by AI."""
    SECTION_KEYS = [
        ("wettelijke_basis", "Wettelijke basis"),
        ("clientenonderzoek", "Cliëntenonderzoek"),
        ("risicobeleid", "Risicobeleid kantoorniveau"),
        ("pep_sancties", "PEP, sancties en herkomst middelen"),
        ("verscherpt_onderzoek", "Verscherpt cliëntenonderzoek"),
        ("meldplicht", "Meldplicht en transactiemonitoring"),
        ("herbeoordeling", "Periodieke herbeoordeling"),
        ("compliance_infra", "Intern compliance-infrastructuur"),
        ("bft_bevindingen", "BFT inspectie-bevindingen"),
        ("actuele_wetgeving", "Actuele wet- en regelgeving"),
    ]
    STATUS_CHOICES = [
        ("default", "Standaard"),
        ("checking", "Wordt gecontroleerd"),
        ("updated", "Bijgewerkt door AI"),
        ("error", "Fout bij update"),
    ]

    key = models.CharField(max_length=50, unique=True, choices=SECTION_KEYS)
    title = models.CharField(max_length=200)
    body = models.TextField()
    ai_summary = models.TextField(blank=True, default="")
    ai_sources = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="default")
    last_checked = models.DateTimeField(null=True, blank=True)
    last_check_job = models.ForeignKey(ScanJob, on_delete=models.SET_NULL, null=True, blank=True)
    can_ai_update = models.BooleanField(default=True)
    office_action_required = models.BooleanField(default=False)
    office_action_description = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class ComplianceSectionVersion(models.Model):
    """Stores a previous version of a ComplianceSection body whenever it changes."""
    section = models.ForeignKey(ComplianceSection, on_delete=models.CASCADE, related_name="versions")
    body = models.TextField()
    changed_by = models.CharField(max_length=50)  # "ai" or "user"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.section.title} — {self.changed_by} — {self.created_at:%Y-%m-%d %H:%M}"


# ---------------------------------------------------------------------------
# Sales / CRM models
# ---------------------------------------------------------------------------

class ProspectGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    slug = models.SlugField(max_length=200, unique=True)
    owner = models.ForeignKey(
        django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="prospect_groups", null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            _save_with_unique_slug(self, slug_field_max=190, slug_source_attr="name")
            return
        super().save(*args, **kwargs)


class Prospect(models.Model):
    STATUS_CHOICES = [
        ("new", "Nieuw"),
        ("not_contacted", "Niet benaderd"),
        ("contacted", "Benaderd"),
        ("interested", "Geïnteresseerd"),
        ("not_interested", "Geen interesse"),
        ("client", "Klant"),
    ]
    CHANNEL_CHOICES = [
        ("", "—"),
        ("linkedin", "LinkedIn"),
        ("phone", "Telefoon"),
        ("email", "E-mail"),
        ("contact_form", "Contactformulier"),
        ("post", "Post"),
        ("visit", "Bezoek"),
        ("paid_ads", "Betaalde reclame"),
        ("other", "Anders"),
    ]

    place_id = models.CharField(max_length=300, blank=True, default="")
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    website = models.CharField(max_length=500, blank=True, default="")
    linkedin_url = models.URLField(max_length=500, blank=True, default="")
    google_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    google_reviews_count = models.IntegerField(default=0)
    business_type = models.CharField(max_length=200, blank=True, default="")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    groups = models.ManyToManyField(ProspectGroup, blank=True, related_name="prospects")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    contact_channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, blank=True, default="")
    contacted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    contact_first_name = models.CharField(max_length=100, blank=True, default="")
    contact_last_name = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(blank=True, default="", db_index=True)
    AANHEF_CHOICES = [
        ("", "—"),
        ("Geachte heer", "Geachte heer"),
        ("Geachte mevrouw", "Geachte mevrouw"),
        ("Geachte heer/mevrouw", "Geachte heer/mevrouw"),
        ("Beste", "Beste"),
    ]
    aanhef = models.CharField(max_length=30, choices=AANHEF_CHOICES, blank=True, default="")
    assigned_template = models.ForeignKey(
        "ResponseTemplate", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_prospects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["place_id"],
                condition=~models.Q(place_id=""),
                name="unique_place_id_when_set",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            _save_with_unique_slug(self, slug_field_max=290, slug_source_attr="name")
            return
        super().save(*args, **kwargs)


class PlacesSearch(models.Model):
    query = models.CharField(max_length=300)
    location = models.CharField(max_length=200, blank=True, default="")
    radius_km = models.IntegerField(default=10)
    business_type = models.CharField(max_length=100, blank=True, default="")
    results_count = models.IntegerField(default=0)
    target_group = models.ForeignKey(ProspectGroup, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Places searches"

    def __str__(self):
        return f"{self.query} ({self.location})"


class SalesDiary(models.Model):
    """Daily sales diary entry with goals, results and notes."""
    date = models.DateField(unique=True)
    goals = models.TextField(blank=True, default="")
    results = models.TextField(blank=True, default="")
    notes = models.TextField(blank=True, default="")
    prospects_target = models.IntegerField(default=0)
    prospects_contacted_actual = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_prospects_target(self):
        return self.diary_goals.aggregate(t=Sum('prospects_target'))['t'] or 0

    @property
    def total_prospects_contacted(self):
        return self.diary_goals.aggregate(t=Sum('prospects_contacted_actual'))['t'] or 0

    @property
    def prospect_progress_pct(self):
        target = self.total_prospects_target
        if target <= 0:
            return 0
        return min(round(self.total_prospects_contacted / target * 100), 100)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Sales diary entries"

    def __str__(self):
        return f"Dagboek {self.date:%Y-%m-%d}"


class DiaryGoal(models.Model):
    diary = models.ForeignKey(SalesDiary, on_delete=models.CASCADE, related_name="diary_goals")
    description = models.CharField(max_length=255, blank=True, default="")
    prospects_target = models.IntegerField(default=0)
    prospects_contacted_actual = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.diary} — {self.description[:60]}"


class TemplateCategory(models.Model):
    """Manageable categories for response templates."""
    COLOR_CHOICES = [
        ("blue", "Blauw"), ("indigo", "Indigo"), ("purple", "Paars"),
        ("emerald", "Groen"), ("amber", "Oranje"), ("rose", "Roze"),
        ("teal", "Teal"), ("sky", "Lichtblauw"),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default="indigo")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            _save_with_unique_slug(self, slug_field_max=120, slug_source_attr="name")
            return
        super().save(*args, **kwargs)


class ResponseTemplate(models.Model):
    """Pre-defined response messages for prospects, grouped by category."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(TemplateCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="templates")
    subject = models.CharField(max_length=300, blank=True, default="")
    body = models.TextField()
    html_template = models.TextField(blank=True, default="")
    is_starred = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"[{self.category.name if self.category else 'Geen'}] {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            _save_with_unique_slug(self, slug_field_max=190, slug_source_attr="name")
            return
        super().save(*args, **kwargs)

    def interpolate(self, prospect):
        """Return (subject, body, html_body) with prospect placeholders replaced."""
        from django.utils.html import escape as html_escape

        replacements = {
            "{aanhef}": prospect.aanhef or "",
            "{voornaam}": prospect.contact_first_name or "",
            "{achternaam}": prospect.contact_last_name or "",
            "{bedrijfsnaam}": prospect.name or "",
        }
        subject = self.subject
        body = self.body
        html_body = self.html_template
        for placeholder, value in replacements.items():
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)
            if html_body:
                html_body = html_body.replace(placeholder, html_escape(value))
        # Clean up spaces before punctuation (from empty replacements)
        subject = re.sub(r'\s+([,.])', r'\1', subject)
        body = re.sub(r'\s+([,.])', r'\1', body)
        if html_body:
            html_body = re.sub(r'\s+([,.])', r'\1', html_body)
        return subject, body, html_body

    @staticmethod
    def strip_html_to_text(html):
        """Extract readable text from an HTML string."""
        from html.parser import HTMLParser
        from html import unescape

        class _TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.parts = []
                self._skip = False

            def handle_starttag(self, tag, attrs):
                self._skip = tag in ("style", "head", "title")
                if tag in ("br", "tr", "p", "div", "li", "h1", "h2", "h3"):
                    self.parts.append("\n")

            def handle_endtag(self, tag):
                self._skip = False

            def handle_data(self, data):
                if not self._skip:
                    self.parts.append(data)

        extractor = _TextExtractor()
        extractor.feed(unescape(html))
        text = "".join(extractor.parts)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def get_text_preview(self):
        """Extract readable text from html_template for preview display."""
        if not self.html_template:
            return self.body
        return self.strip_html_to_text(self.html_template)


class ProspectResponse(models.Model):
    """Tracks which template was sent to which prospect, and when."""
    prospect = models.ForeignKey("Prospect", on_delete=models.CASCADE, related_name="responses")
    template = models.ForeignKey(ResponseTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        tpl = self.template.name if self.template else "—"
        return f"{self.prospect.name} ← {tpl} ({self.sent_at:%d-%m-%Y})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class TrackingEvent(models.Model):
    """Tracks email opens and clicks via local tracking endpoints."""
    token = models.UUIDField(db_index=True)  # = ProspectResponse.tracking_token
    event_type = models.CharField(max_length=10)  # "open" or "click"
    url = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token", "event_type"]),
        ]

    def __str__(self):
        return f"[{self.event_type}] {self.token} — {self.created_at:%Y-%m-%d %H:%M}"


class ComplianceReport(models.Model):
    """Archive entry for a completed WWFT compliance check."""
    REPORT_TYPES = [
        ("investigation", "Persoonsonderzoek"),
        ("section_check", "Sectie-update"),
        ("legislation_search", "Wetgeving zoeken"),
    ]
    RISK_LEVELS = [
        ("low", "Laag"),
        ("medium", "Midden"),
        ("high", "Hoog"),
        ("unknown", "Onbekend"),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    entity_name = models.CharField(max_length=300, blank=True, default="")
    section = models.ForeignKey(ComplianceSection, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.ForeignKey(ScanJob, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField()
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default="unknown")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_report_type_display()}] {self.entity_name or 'Sectie-check'} — {self.created_at:%Y-%m-%d %H:%M}"


class Vacancy(models.Model):
    """Job vacancy scraped from external sources (Indeed, Jooble, Adzuna)."""
    SOURCE_CHOICES = [
        ("jooble", "Jooble"),
        ("adzuna", "Adzuna"),
        ("careerjet", "CareerJet"),
    ]
    CATEGORY_CHOICES = [
        ("financieel", "Financieel administratie"),
        ("data_analyse", "Data-analyse"),
        ("ict", "ICT en netwerken"),
        ("zzp_admin", "ZZP Administratie"),
        ("automatisering", "Automatisering"),
        ("", "Overig"),
    ]

    external_id = models.CharField(max_length=300, unique=True)
    title = models.CharField(max_length=500)
    company_name = models.CharField(max_length=300, db_index=True)
    location = models.CharField(max_length=300, blank=True, default="")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, default="")
    description = models.TextField(blank=True, default="")
    salary = models.CharField(max_length=200, blank=True, default="")
    source_url = models.URLField(blank=True, default="", max_length=500)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, db_index=True)
    published_date = models.DateField(null=True, blank=True)
    prospect = models.ForeignKey(
        Prospect, on_delete=models.SET_NULL, null=True, blank=True, related_name="vacancies",
    )
    relevance_score = models.IntegerField(default=0)  # 0-100 match score
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_date", "-created_at"]
        verbose_name_plural = "Vacancies"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(relevance_score__gte=0, relevance_score__lte=100),
                name="relevance_score_range",
            ),
        ]

    def __str__(self):
        return f"{self.title} — {self.company_name}"


class VacancySearch(models.Model):
    """Logs each vacancy search query for structural monitoring."""
    query = models.CharField(max_length=500)
    location = models.CharField(max_length=200, blank=True, default="")
    sources_used = models.CharField(max_length=200, blank=True, default="")
    results_count = models.IntegerField(default=0)
    companies_found = models.IntegerField(default=0)
    new_companies = models.IntegerField(default=0)
    avg_relevance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Vacancy searches"

    def __str__(self):
        return f"{self.query} ({self.location}) — {self.results_count} results"


class BusinessType(models.Model):
    """Manageable business types for Google Places search."""
    google_type = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)

    class Meta:
        ordering = ["label"]

    def __str__(self):
        return self.label


# ---------------------------------------------------------------------------
# API Usage Tracking
# ---------------------------------------------------------------------------

class APIUsageLog(models.Model):
    """Centraal log van alle betaalde API-aanroepen (LLM tokens + Google Places)."""
    SERVICE_CHOICES = [
        ("gemini", "Google Gemini"),
        ("anthropic", "Anthropic Claude"),
        ("openai", "OpenAI"),
        ("google_places", "Google Places API"),
    ]

    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, db_index=True)
    job = models.ForeignKey("ScanJob", on_delete=models.SET_NULL, null=True, blank=True, related_name="api_usage_logs")
    description = models.CharField(max_length=300, blank=True, default="")

    # Token metrics (for LLM APIs)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    # Cost
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    # For non-LLM APIs (Places)
    api_calls = models.IntegerField(default=1)

    # Model info (for LLM calls)
    model_name = models.CharField(max_length=100, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["service", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_service_display()}] {self.description[:60]} — ${self.estimated_cost}"


# ---------------------------------------------------------------------------
# RJ Richtlijnen voor de Jaarverslaggeving
# ---------------------------------------------------------------------------

class RJHoofdstuk(models.Model):
    """Een hoofdstuk uit de RJ (bijv. B2 Materiële vaste activa)."""
    AFDELING_CHOICES = [
        ("M", "Microrechtspersonen"),
        ("A", "Algemeen"),
        ("B", "Jaarrekening"),
        ("C", "Bijzondere kleine rechtspersonen"),
        ("D", "Bijlagen"),
    ]

    code = models.CharField(max_length=10, unique=True)  # "B2", "A1", "M1"
    titel = models.CharField(max_length=300)
    afdeling = models.CharField(max_length=1, choices=AFDELING_CHOICES)
    beschrijving = models.TextField(blank=True, default="")
    editie = models.CharField(max_length=10, default="2022")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "RJ Hoofdstuk"
        verbose_name_plural = "RJ Hoofdstukken"

    def __str__(self):
        return f"{self.code} — {self.titel}"


class RJSectie(models.Model):
    """Een paragraaf binnen een RJ-hoofdstuk (bijv. § B2.1 Materiële vaste activa)."""
    hoofdstuk = models.ForeignKey(RJHoofdstuk, on_delete=models.CASCADE, related_name="secties")
    paragraaf = models.CharField(max_length=20)  # "B2.1", "M1.1"
    titel = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["hoofdstuk", "paragraaf"], name="unique_rj_sectie_paragraaf"),
        ]
        verbose_name = "RJ Sectie"
        verbose_name_plural = "RJ Secties"

    def __str__(self):
        return f"§ {self.paragraaf} — {self.titel}"


class RJAlinea(models.Model):
    """Een individuele alinea/bepaling uit de RJ (bijv. B2.101)."""
    from pgvector.django import VectorField

    sectie = models.ForeignKey(RJSectie, on_delete=models.CASCADE, related_name="alineas")
    nummer = models.CharField(max_length=10)  # "101", "133d"
    sub_onderwerp = models.CharField(max_length=200, blank=True, default="")
    inhoud = models.TextField()
    embedding = VectorField(dimensions=384, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["sectie", "nummer"], name="unique_rj_alinea_nummer"),
        ]
        verbose_name = "RJ Alinea"
        verbose_name_plural = "RJ Alinea's"

    def __str__(self):
        return f"{self.sectie.paragraaf}.{self.nummer}"

    @property
    def referentie(self):
        return f"{self.sectie.paragraaf}.{self.nummer}"


class RJRubriekMapping(models.Model):
    """Koppelt jaarrekening-rubrieken aan relevante RJ-hoofdstukken."""
    rubriek_naam = models.CharField(max_length=200, unique=True)
    rubriek_code = models.CharField(max_length=20, blank=True, default="")
    hoofdstukken = models.ManyToManyField(RJHoofdstuk, related_name="rubrieken")
    beschrijving = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["rubriek_naam"]
        verbose_name = "RJ Rubriek Mapping"
        verbose_name_plural = "RJ Rubriek Mappings"

    def __str__(self):
        return self.rubriek_naam


# ---------------------------------------------------------------------------
# Fiscale Wetgeving (VPB / DB / AWR)
# ---------------------------------------------------------------------------

class FiscaleWet(models.Model):
    """Een fiscale wet (bijv. Wet Vpb 1969, Wet DB 1965, AWR)."""
    code = models.CharField(max_length=20)  # "vpb1969", "db1965", "awr"
    naam = models.CharField(max_length=300)  # "Wet op de vennootschapsbelasting 1969"
    afkorting = models.CharField(max_length=50)  # "Wet Vpb 1969"
    bwb_id = models.CharField(max_length=30, blank=True, default="")  # "BWBR0002672"
    versie_datum = models.CharField(
        max_length=10, default="2024-01-01", db_index=True,
        help_text="Geldigheids-datum, bijv. '2025-01-01'",
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Fiscale Wet"
        verbose_name_plural = "Fiscale Wetten"
        constraints = [
            models.UniqueConstraint(fields=["code", "versie_datum"], name="unique_wet_code_versie"),
        ]

    def __str__(self):
        return self.afkorting


class FiscaalHoofdstuk(models.Model):
    """Een hoofdstuk binnen een fiscale wet."""
    wet = models.ForeignKey(FiscaleWet, on_delete=models.CASCADE, related_name="hoofdstukken")
    nummer = models.CharField(max_length=20)  # "II", "V", "IIA"
    titel = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["wet", "nummer"], name="unique_fiscaal_hoofdstuk"),
        ]
        verbose_name = "Fiscaal Hoofdstuk"
        verbose_name_plural = "Fiscale Hoofdstukken"

    def __str__(self):
        return f"Hoofdstuk {self.nummer} — {self.titel}"


class FiscaalArtikel(models.Model):
    """Een artikel uit een fiscale wet (bijv. Artikel 13 Wet Vpb 1969)."""
    hoofdstuk = models.ForeignKey(FiscaalHoofdstuk, on_delete=models.CASCADE, related_name="artikelen")
    nummer = models.CharField(max_length=20)  # "8", "13", "15b", "10a"
    titel = models.CharField(max_length=300, blank=True, default="")
    volledige_tekst = models.TextField(blank=True, default="")
    is_vervallen = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["hoofdstuk", "nummer"], name="unique_fiscaal_artikel"),
        ]
        verbose_name = "Fiscaal Artikel"
        verbose_name_plural = "Fiscale Artikelen"

    def __str__(self):
        wet = self.hoofdstuk.wet.afkorting
        label = f"Art. {self.nummer} {wet}"
        if self.titel:
            label += f" — {self.titel}"
        return label

    @property
    def referentie(self):
        return f"art. {self.nummer} {self.hoofdstuk.wet.afkorting}"


class FiscaalLid(models.Model):
    """Een lid (paragraaf) binnen een fiscaal artikel — atomaire zoekeenheid met embedding."""
    from pgvector.django import VectorField

    artikel = models.ForeignKey(FiscaalArtikel, on_delete=models.CASCADE, related_name="leden")
    nummer = models.CharField(max_length=10)  # "1", "2", "3a"
    inhoud = models.TextField()
    embedding = VectorField(dimensions=384, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["artikel", "nummer"], name="unique_fiscaal_lid"),
        ]
        verbose_name = "Fiscaal Lid"
        verbose_name_plural = "Fiscale Leden"

    def __str__(self):
        return f"{self.artikel.referentie} lid {self.nummer}"

    @property
    def referentie(self):
        return f"{self.artikel.referentie} lid {self.nummer}"


class FiscaalConceptMapping(models.Model):
    """Koppelt fiscale concepten aan relevante wetsartikelen."""
    concept_naam = models.CharField(max_length=200, unique=True)
    artikelen = models.ManyToManyField(FiscaalArtikel, related_name="concepten")
    trefwoorden = models.TextField(blank=True, default="")  # comma-separated
    beschrijving = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["concept_naam"]
        verbose_name = "Fiscaal Concept Mapping"
        verbose_name_plural = "Fiscale Concept Mappings"

    def __str__(self):
        return self.concept_naam


# ---------------------------------------------------------------------------
# VPB Boek ("Wegwijs in de Vennootschapsbelasting")
# ---------------------------------------------------------------------------

class VpbBoekHoofdstuk(models.Model):
    """Een hoofdstuk uit het boek 'Wegwijs in de Vennootschapsbelasting'."""
    nummer = models.CharField(max_length=10)  # "1", "2", "3"
    titel = models.CharField(max_length=300)
    editie = models.CharField(
        max_length=10, default="2023", db_index=True,
        help_text="Editie/boekjaar, bijv. '2023' voor 18e druk",
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "VPB Boek Hoofdstuk"
        verbose_name_plural = "VPB Boek Hoofdstukken"
        constraints = [
            models.UniqueConstraint(fields=["nummer", "editie"], name="unique_boek_nummer_editie"),
        ]

    def __str__(self):
        return f"H{self.nummer} — {self.titel}"


class VpbBoekSectie(models.Model):
    """Een paragraaf/sectie binnen een boek-hoofdstuk."""
    hoofdstuk = models.ForeignKey(VpbBoekHoofdstuk, on_delete=models.CASCADE, related_name="secties")
    paragraaf = models.CharField(max_length=20)  # "1.1", "3.2.1"
    titel = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["hoofdstuk", "paragraaf"], name="unique_vpbboek_sectie"),
        ]
        verbose_name = "VPB Boek Sectie"
        verbose_name_plural = "VPB Boek Secties"

    def __str__(self):
        return f"§ {self.paragraaf} — {self.titel}"


class VpbBoekPassage(models.Model):
    """Een tekstpassage uit het VPB-boek — atomaire zoekeenheid met embedding."""
    from pgvector.django import VectorField

    sectie = models.ForeignKey(VpbBoekSectie, on_delete=models.CASCADE, related_name="passages")
    volgnummer = models.PositiveIntegerField()
    inhoud = models.TextField()
    pagina_start = models.PositiveIntegerField(null=True, blank=True)
    embedding = VectorField(dimensions=384, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["sectie", "volgnummer"], name="unique_vpbboek_passage"),
        ]
        verbose_name = "VPB Boek Passage"
        verbose_name_plural = "VPB Boek Passages"

    def __str__(self):
        return f"{self.sectie.paragraaf} #{self.volgnummer}"
