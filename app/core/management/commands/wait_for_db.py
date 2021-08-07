import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available."""

    def handle(self, *args, **options):
        """The handle is run whenever the wait_for_db command is run."""

        self.stdout.write('Waiting for the database...')

        db_conn = None
        while not db_conn:
            try:
                # connections['default'] returns a connection to default db.
                # If the connection is unavailable, OperationalError is thrown.
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write(
                    'The database is not available, waiting for 1 second...'
                )
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('The database is available!'))
