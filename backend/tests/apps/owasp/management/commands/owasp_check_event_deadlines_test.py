"""Tests for event deadline check management command."""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.owasp.management.commands.owasp_check_event_deadlines import Command


class TestCheckEventDeadlines:
    """Test owasp_check_event_deadlines management command."""

    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.publish_event_notification")
    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.Event")
    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.timezone")
    def test_finds_events_at_reminder_days(self, mock_tz, mock_event_cls, mock_publish):
        """Test that the command checks for events at 7, 3, and 1 day thresholds."""
        today = timezone.now().date()
        mock_tz.now.return_value.date.return_value = today
        mock_tz.timedelta = timedelta

        mock_event_cls.objects.filter.return_value = []

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle()

        # Should query for 3 different dates (7, 3, 1 days from now)
        assert mock_event_cls.objects.filter.call_count == 3

        expected_dates = [today + timedelta(days=d) for d in (7, 3, 1)]
        actual_dates = [
            call.kwargs["start_date"] for call in mock_event_cls.objects.filter.call_args_list
        ]
        assert actual_dates == expected_dates

    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.publish_event_notification")
    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.Event")
    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.timezone")
    def test_publishes_reminder_for_matching_events(self, mock_tz, mock_event_cls, mock_publish):
        """Test that matching events trigger deadline_reminder notifications."""
        today = timezone.now().date()
        mock_tz.now.return_value.date.return_value = today
        mock_tz.timedelta = timedelta

        mock_event = MagicMock()
        mock_event.name = "AppSec Days"

        # Only the 7-day query returns an event
        mock_event_cls.objects.filter.side_effect = [[mock_event], [], []]

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle()

        mock_publish.assert_called_once_with(mock_event, "deadline_reminder", days_remaining=7)

    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.publish_event_notification")
    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.Event")
    @patch("apps.owasp.management.commands.owasp_check_event_deadlines.timezone")
    def test_no_events_found(self, mock_tz, mock_event_cls, mock_publish):
        """Test that no notifications are sent when no events match."""
        today = timezone.now().date()
        mock_tz.now.return_value.date.return_value = today
        mock_tz.timedelta = timedelta

        mock_event_cls.objects.filter.return_value = []

        command = Command()
        command.stdout = MagicMock()
        command.style = MagicMock()
        command.style.SUCCESS = lambda x: x

        command.handle()

        mock_publish.assert_not_called()
