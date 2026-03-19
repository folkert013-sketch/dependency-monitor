import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)


def _configure_sqlite(sender, connection, **kwargs):
    """Enable WAL mode and set busy timeout for SQLite connections (K4)."""
    if connection.vendor == "sqlite":
        cursor = connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA busy_timeout=5000;")


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

    def ready(self):
        # K4: Configure SQLite WAL mode for better concurrent write support
        from django.db.backends.signals import connection_created
        connection_created.connect(_configure_sqlite)

        # B4: Warn about missing API keys at startup (not crash, just warn)
        missing = []
        if not os.environ.get("GEMINI_API_KEY"):
            missing.append("GEMINI_API_KEY")
        if missing:
            logger.warning(
                "Missing API keys: %s — scans will fail until configured.",
                ", ".join(missing),
            )
