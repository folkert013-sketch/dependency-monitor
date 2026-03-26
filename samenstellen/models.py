from pathlib import Path

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Fase — definieert het "wat" per fase van de samenstelopdracht
# ---------------------------------------------------------------------------

class Fase(models.Model):
    """Een fase van de samenstelopdracht conform NV COS 4410.

    Legt vast: doelen, randvoorwaarden, referenties naar wet- en regelgeving,
    en welk AI Team de werkzaamheden uitvoert.
    """

    FASE_CHOICES = [
        ("randvoorwaarden", "Randvoorwaarden"),
        ("aanvaarding", "Aanvaarding en continuering"),
        ("inzicht", "Inzicht"),
        ("samenstellen", "Samenstellen"),
        ("nalezen", "Nalezen"),
        ("verklaring", "Samenstellingsverklaring"),
    ]
    RUN_CHOICES = [
        (1, "Run 1 — Analyse"),
        (2, "Run 2 — Afsluiting"),
    ]

    fase_key = models.CharField(max_length=30, choices=FASE_CHOICES, unique=True)
    naam = models.CharField(max_length=100)
    beschrijving = models.TextField(blank=True, default="")
    doelen = models.TextField(blank=True, default="")
    randvoorwaarden = models.TextField(blank=True, default="")
    referenties = models.TextField(blank=True, default="")
    run_nummer = models.IntegerField(choices=RUN_CHOICES, default=1)
    order = models.PositiveIntegerField(default=0)
    team = models.ForeignKey(
        "dashboard.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="samenstellen_fasen",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Fase"
        verbose_name_plural = "Fasen"

    def __str__(self):
        return self.naam


# ---------------------------------------------------------------------------
# Opdracht — een samenstelopdracht voor een specifieke klant
# ---------------------------------------------------------------------------

class Opdracht(models.Model):
    """Een samenstelopdracht-instance per klant/boekjaar."""

    STATUS_CHOICES = [
        ("nieuw", "Nieuw"),
        ("run1_bezig", "Analyse bezig"),
        ("run1_klaar", "Analyse afgerond"),
        ("run2_bezig", "Nalezen bezig"),
        ("afgerond", "Afgerond"),
    ]

    client_naam = models.CharField(max_length=200)
    boekjaar = models.CharField(max_length=10, default="2025")
    rechtsvorm = models.CharField(max_length=50, default="BV")
    sector = models.CharField(max_length=200, blank=True, default="")
    verslaggevingsstelsel = models.CharField(max_length=50, default="RJ")
    concept_pdf = models.CharField(max_length=500, blank=True, default="")
    definitieve_pdf = models.CharField(max_length=500, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="nieuw", db_index=True,
    )
    run1_job = models.ForeignKey(
        "dashboard.ScanJob", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    run2_job = models.ForeignKey(
        "dashboard.ScanJob", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Samenstelopdracht"
        verbose_name_plural = "Samenstelopdrachten"

    def __str__(self):
        return f"{self.client_naam} — {self.boekjaar}"

    @property
    def dossier_path(self) -> Path:
        from django.conf import settings

        slug = slugify(self.client_naam) or "opdracht"
        return Path(settings.MEDIA_ROOT) / "dossiers" / f"{self.pk}_{slug}"

    def ensure_dossier_dirs(self):
        """Maak de dossiermap en fase-submappen aan."""
        base = self.dossier_path
        base.mkdir(parents=True, exist_ok=True)
        for key, _label in Fase.FASE_CHOICES:
            (base / key).mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# FaseResultaat — AI-resultaat per fase per opdracht
# ---------------------------------------------------------------------------

class FaseResultaat(models.Model):
    """Slaat het AI-resultaat op van een specifieke fase voor een opdracht."""

    STATUS_CHOICES = [
        ("pending", "Wachten"),
        ("running", "Bezig"),
        ("completed", "Afgerond"),
        ("failed", "Mislukt"),
    ]

    opdracht = models.ForeignKey(
        Opdracht, on_delete=models.CASCADE, related_name="fase_resultaten",
    )
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    resultaat = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    token_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["fase__order"]
        unique_together = [("opdracht", "fase")]
        verbose_name = "Fase-resultaat"
        verbose_name_plural = "Fase-resultaten"

    def __str__(self):
        return f"{self.opdracht} — {self.fase.naam}"


# ---------------------------------------------------------------------------
# Document — dossiervorming, documenten per fase
# ---------------------------------------------------------------------------

class Document(models.Model):
    """Een document gekoppeld aan een opdracht, optioneel aan een specifieke fase."""

    opdracht = models.ForeignKey(
        Opdracht, on_delete=models.CASCADE, related_name="documenten",
    )
    fase = models.ForeignKey(
        Fase, on_delete=models.SET_NULL, null=True, blank=True,
    )
    naam = models.CharField(max_length=300)
    bestand = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documenten"

    def __str__(self):
        return self.naam
