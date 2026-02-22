from django.db import models


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
