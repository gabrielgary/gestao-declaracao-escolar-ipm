import os
import django
import sys

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Nota

def check_grades():
    total_notas = Nota.objects.count()
    notas_com_tipo = Nota.objects.filter(tipo_nota__isnull=False).count()
    print(f"Total: {total_notas}, Com Tipo: {notas_com_tipo}")

if __name__ == "__main__":
    check_grades()
