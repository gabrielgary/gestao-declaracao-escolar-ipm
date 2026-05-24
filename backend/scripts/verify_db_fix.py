import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

def verify():
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'solicitacao_documento';")
        cols = [r[0] for r in cursor.fetchall()]
        
        result = "FAILURE: Column missing"
        if 'canal_pagamento_rup' in cols:
            result = "SUCCESS: Column exists"
        
        with open('db_check_result.txt', 'w') as f:
            f.write(result)

if __name__ == "__main__":
    verify()
