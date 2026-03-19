from django.conf import settings
from django.db import models


class EmailSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_settings")
    smtp_user = models.EmailField(help_text="Afzender e-mailadres")
    display_name = models.CharField(max_length=100, blank=True, default="", help_text="Weergavenaam in From header")
    graph_tenant_id = models.CharField(max_length=100, blank=True, default="", help_text="Azure AD Tenant ID")
    graph_client_id = models.CharField(max_length=100, blank=True, default="", help_text="Azure AD Client ID")
    graph_client_secret = models.CharField(max_length=200, blank=True, default="", help_text="Azure AD Client Secret")

    class Meta:
        verbose_name = "E-mail instellingen"
        verbose_name_plural = "E-mail instellingen"

    def __str__(self):
        return f"E-mail instellingen — {self.user.username}"

    @property
    def is_configured(self):
        return bool(self.graph_tenant_id and self.graph_client_id and self.graph_client_secret and self.smtp_user)

    @property
    def from_header(self):
        if self.display_name:
            return f"{self.display_name} <{self.smtp_user}>"
        return self.smtp_user
