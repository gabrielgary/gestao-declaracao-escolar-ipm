import os
import sys
import django
from django.db import connection

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

with connection.cursor() as cursor:
    try:
        cursor.execute("ALTER TABLE documento ADD COLUMN codigo_seguranca VARCHAR(20) NULL;")
        print("✅ Coluna 'codigo_seguranca' adicionada com sucesso na tabela documento!")
    except Exception as e:
        print(f"⚠️ Erro ao adicionar coluna (pode ser que já exista): {e}")
