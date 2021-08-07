from django.test import TestCase
from unittest.mock import patch
from django.db.utils import OperationalError
from django.core.management import call_command


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Tests waiting for the database when the database is available.
           Overrides the behavior of the ConnectionHandler to make it
           return True (not throws an exception). Therefore, management
           commands or call commands continue to execution."""

        # Mock the ConnectionHandler to return true everytime it's called.
        # Data retrival is handled through the __getitem__ method.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True

            call_command('wait_for_db')

            # Check that the __getitem__ has been called only once.
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=None)
    def test_wait_for_db(self, ts):
        """Tests waiting for the db: Checks that the wait_for_db command tries
           to connect the db five times and in the sixth trial, it'll succeed.
           It basically checks to see if the ConnectionHandler raises the
           OperationalError (it does, when db is not available). If it does, it
           waits a second, and tries again. It is possible to remove this delay
           by using the patch decorator. The patch replaces the behavior of
           time.sleep with a mock function that returns True."""

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Set side effects to make it raise OperationalError in the
            # first five trials, and to make it succeed in the sixth trial.
            gi.side_effect = [OperationalError] * 5 + [True]

            call_command('wait_for_db')

            self.assertEqual(gi.call_count, 6)
