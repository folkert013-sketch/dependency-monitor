import uuid

from django.db import IntegrityError, models
from django.db.models import Sum
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
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="variables")
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    input_type = models.CharField(max_length=10, choices=INPUT_TYPE_CHOICES, default="text")
    default_value = models.TextField(blank=True, default="")
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = [("team", "name")]

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

    class Meta:
        ordering = ["order"]

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
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    job_type = models.CharField(max_length=15, choices=JOB_TYPE_CHOICES, default="dependency")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")
    run_variables = models.JSONField(default=dict, blank=True)
    progress_message = models.CharField(max_length=300, default="Scan starten...")
    active_agent = models.CharField(max_length=100, blank=True, default="")
    tasks_completed = models.IntegerField(default=0)
    token_count = models.IntegerField(default=0)
    report = models.ForeignKey("Report", on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


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
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    sources = models.JSONField(default=list, blank=True, help_text="Bron-URLs")
    quality_score = models.IntegerField(default=5, help_text="Kwaliteitsscore 1-10 van reviewer-agent")
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    contact_channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, blank=True, default="")
    contacted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    contact_first_name = models.CharField(max_length=100, blank=True, default="")
    contact_last_name = models.CharField(max_length=100, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    AANHEF_CHOICES = [
        ("", "—"),
        ("Geachte heer", "Geachte heer"),
        ("Geachte mevrouw", "Geachte mevrouw"),
        ("Beste", "Beste"),
    ]
    aanhef = models.CharField(max_length=30, choices=AANHEF_CHOICES, blank=True, default="")
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
        return subject, body, html_body


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


class BusinessType(models.Model):
    """Manageable business types for Google Places search."""
    google_type = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=200)

    class Meta:
        ordering = ["label"]

    def __str__(self):
        return self.label
