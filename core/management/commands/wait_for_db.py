import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

from psycopg2 import OperationalError as Psycopyg2OpError


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"].cursor()
            except (OperationalError, Psycopyg2OpError):
                self.stdout.write(
                    "Database unavailable, waiting for 1 second..."
                )
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))
