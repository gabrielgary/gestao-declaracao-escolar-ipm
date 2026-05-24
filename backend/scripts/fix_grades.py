import os
import django
import sys

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Nota
from django.db import transaction

def fix_grades():
    print("Iniciando correção de notas...")
    
    map_tipo_nota = {
        'Avaliação Continua': 'MAC',
        'Prova do Professor': 'PP',
        'Prova Trimestral': 'PT'
    }
    
    notas = Nota.objects.all()
    count_updated = 0
    count_skipped = 0
    
    with transaction.atomic():
        for nota in notas:
            if not nota.tipo_nota and nota.tipo_avaliacao:
                tipo_nota_mapped = map_tipo_nota.get(nota.tipo_avaliacao)
                if tipo_nota_mapped:
                    nota.tipo_nota = tipo_nota_mapped
                    nota.save()
                    count_updated += 1
                else:
                    print(f"Aviso: Nota ID {nota.pk} tem tipo_avaliacao desconhecido: {nota.tipo_avaliacao}")
            else:
                count_skipped += 1
                
    print(f"Correção concluída!")
    print(f"Notas atualizadas: {count_updated}")
    print(f"Notas ignoradas (já corretas ou sem tipo): {count_skipped}")

if __name__ == "__main__":
    fix_grades()
