import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

def check_columns():
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'solicitacao_documento';")
        columns = cursor.fetchall()
        print("Columns in solicitacao_documento:", [col[0] for col in columns])

        cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'apis';")
        migrations = cursor.fetchall()
        print("Applied migrations for apis:", migrations)

if __name__ == "__main__":
    check_columns()
