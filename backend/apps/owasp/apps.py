"""Owasp app config."""

from django.apps import AppConfig


class OwaspConfig(AppConfig):
    """Owasp app config."""

    name = "apps.owasp"

    def ready(self):
        """Import signals when app is ready."""
        import apps.owasp.signals.chapter
        import apps.owasp.signals.event
        import apps.owasp.signals.snapshot  # noqa: F401
