from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class MockConnection:
    # TODO: review this
    def cursor(*args, **kwargs):
        return True


class CommandTests(TestCase):
    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.return_value = MockConnection()
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 1)

    @patch("time.sleep", return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            gi.side_effect = [OperationalError] * 5 + [MockConnection()]
            call_command("wait_for_db")

            self.assertEqual(gi.call_count, 6)
