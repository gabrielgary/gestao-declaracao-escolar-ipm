import os
import django
import sys
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Nota, Aluno
from apis.services.academic_service import AcademicService

def diagnose():
    print("--- DIAGNOSTIC SCRIPT ---")
    
    # 1. Check Data Quality
    total = Nota.objects.count()
    com_tipo = Nota.objects.filter(tipo_nota__isnull=False).count()
    sem_tipo = total - com_tipo
    print(f"Total Notas: {total}")
    print(f"Notas com tipo_nota: {com_tipo}")
    print(f"Notas SEM tipo_nota: {sem_tipo}")
    
    if sem_tipo > 0:
        print("ALERT: Existem notas sem classificação de tipo! O script de correção precisa rodar.")
        
    # 2. Check Service Output for a Student
    # Pegar um aluno que tenha notas
    aluno = Aluno.objects.filter(nota__isnull=False).distinct().first()
    if aluno:
        print(f"\nVerificando boletim para: {aluno.nome_completo} (ID: {aluno.id_aluno})")
        boletim = AcademicService.get_boletim_aluno(aluno)
        
        # Print first discipline result
        if boletim:
            print("Exemplo de estrutura retornada (Primeira Disciplina):")
            print(json.dumps(boletim[0], indent=2, default=str))
        else:
            print("Boletim retornou vazio.")
    else:
        print("Nenhum aluno com notas encontrado.")

if __name__ == "__main__":
    diagnose()
