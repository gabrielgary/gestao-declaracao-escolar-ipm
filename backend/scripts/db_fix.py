import os
import sys
import django
from django.core.management import call_command

# Adiciona o diretório atual ao sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

print("Iniciando migração manual...")
try:
    # Tenta aplicar apenas a migração que criamos
    call_command('migrate', 'apis')
    print("Migração concluída com sucesso!")
except Exception as e:
    print(f"Erro durante a migração: {e}")
