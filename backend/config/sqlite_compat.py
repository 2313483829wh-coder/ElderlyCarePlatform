from django.db import OperationalError
from django.db.backends.signals import connection_created


def configure_sqlite(sender, connection, **kwargs):
    """Improve local sqlite concurrency for admin-write/mobile-read scenarios."""
    if connection.vendor != 'sqlite':
        return

    cursor = connection.cursor()
    try:
        cursor.execute('PRAGMA busy_timeout=5000;')
        try:
            cursor.execute('PRAGMA journal_mode=WAL;')
            cursor.execute('PRAGMA synchronous=NORMAL;')
        except OperationalError:
            pass
    finally:
        cursor.close()


connection_created.connect(configure_sqlite)
