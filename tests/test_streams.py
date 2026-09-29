import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from tap_zendesk.streams import TicketsStream

BOOKMARK = datetime(2026, 9, 28, 12, 9, 25, tzinfo=timezone.utc)


class TestTicketsStreamSkipUnchangedClosed(unittest.TestCase):
    def setUp(self):
        self.tap_mock = MagicMock()
        self.tap_mock.config = {"skip_unchanged_closed_tickets": True}
        self.stream = TicketsStream(self.tap_mock)

    def _post_process(self, row, bookmark=BOOKMARK):
        with patch.object(TicketsStream, "get_starting_timestamp", return_value=bookmark):
            return self.stream.post_process(row, None)

    def test_closed_ticket_not_updated_since_bookmark_is_dropped(self):
        row = {"id": 1, "status": "closed", "updated_at": "2026-07-01T00:01:21Z"}
        self.assertIsNone(self._post_process(row))
        self.assertEqual(self.stream.skipped_unchanged_closed, 1)

    def test_closed_ticket_updated_exactly_at_bookmark_is_kept(self):
        # updated_at has second granularity: a ticket updated in the same second
        # as the bookmark record may only show up in the next export, so it must
        # not be dropped. One duplicate fetch beats a lost record.
        row = {"id": 1, "status": "closed", "updated_at": "2026-09-28T12:09:25+00:00"}
        self.assertEqual(self._post_process(row), row)
        self.assertEqual(self.stream.skipped_unchanged_closed, 0)

    def test_closed_ticket_updated_after_bookmark_is_kept(self):
        row = {"id": 1, "status": "closed", "updated_at": "2026-09-28T12:09:26Z"}
        self.assertEqual(self._post_process(row), row)
        self.assertEqual(self.stream.skipped_unchanged_closed, 0)

    def test_open_ticket_not_updated_since_bookmark_is_kept(self):
        row = {"id": 1, "status": "open", "updated_at": "2026-07-01T00:01:21Z"}
        self.assertEqual(self._post_process(row), row)

    def test_deleted_ticket_not_updated_since_bookmark_is_kept(self):
        row = {"id": 1, "status": "deleted", "updated_at": "2026-07-01T00:01:21Z"}
        self.assertEqual(self._post_process(row), row)

    def test_without_bookmark_nothing_is_dropped(self):
        row = {"id": 1, "status": "closed", "updated_at": "2026-07-01T00:01:21Z"}
        self.assertEqual(self._post_process(row, bookmark=None), row)

    def test_setting_disabled_keeps_everything(self):
        self.tap_mock.config = {"skip_unchanged_closed_tickets": False}
        stream = TicketsStream(self.tap_mock)
        row = {"id": 1, "status": "closed", "updated_at": "2026-07-01T00:01:21Z"}
        with patch.object(TicketsStream, "get_starting_timestamp", return_value=BOOKMARK):
            self.assertEqual(stream.post_process(row, None), row)

    def test_setting_is_off_by_default(self):
        self.tap_mock.config = {}
        stream = TicketsStream(self.tap_mock)
        row = {"id": 1, "status": "closed", "updated_at": "2026-07-01T00:01:21Z"}
        with patch.object(TicketsStream, "get_starting_timestamp", return_value=BOOKMARK):
            self.assertEqual(stream.post_process(row, None), row)
        self.assertEqual(stream.skipped_unchanged_closed, 0)

    def test_naive_bookmark_is_treated_as_utc(self):
        row = {"id": 1, "status": "closed", "updated_at": "2026-09-28T12:09:24Z"}
        self.assertIsNone(self._post_process(row, bookmark=BOOKMARK.replace(tzinfo=None)))

    def test_closed_ticket_one_second_before_bookmark_is_dropped(self):
        row = {"id": 1, "status": "closed", "updated_at": "2026-09-28T12:09:24Z"}
        self.assertIsNone(self._post_process(row))

    def test_missing_updated_at_is_kept(self):
        row = {"id": 1, "status": "closed"}
        self.assertEqual(self._post_process(row), row)


if __name__ == "__main__":
    unittest.main()
