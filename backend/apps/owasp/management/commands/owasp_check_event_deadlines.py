"""Management command to check for approaching event deadlines."""

import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.owasp.models.event import Event
from apps.owasp.utils.notifications import publish_event_notification

logger = logging.getLogger(__name__)

REMINDER_DAYS = (7, 3, 1)


class Command(BaseCommand):
    """Check for events with approaching deadlines and queue reminder notifications."""

    help = "Check for events with approaching deadlines and send reminder notifications."

    def handle(self, *args, **options):
        """Handle execution."""
        self.stdout.write("Checking for approaching event deadlines...")
        today = timezone.now().date()
        total_reminders = 0

        for days in REMINDER_DAYS:
            target_date = today + timezone.timedelta(days=days)
            events = Event.objects.filter(start_date=target_date)

            for event in events:
                self.stdout.write(
                    f"  Event '{event.name}' starts in {days} days ({target_date})"
                )
                publish_event_notification(event, "deadline_reminder", days_remaining=days)
                total_reminders += 1

        self.stdout.write(
            self.style.SUCCESS(f"Queued {total_reminders} deadline reminder(s).")
        )
