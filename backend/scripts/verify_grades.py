import os
import django
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apis.services.academic_service import AcademicService
from apis.models import Aluno, SolicitacaoDocumento

SOLICITACAO_ID = 9

try:
    print(f"--- Debugging Grade Calc for Solicitacao {SOLICITACAO_ID} ---")
    solicitacao = SolicitacaoDocumento.objects.get(id_solicitacao=SOLICITACAO_ID)
    aluno = solicitacao.id_aluno
    classe = solicitacao.classe_solicitada
    
    print(f"Aluno: {aluno.nome_completo}")
    print(f"Classe: {classe}")
    
    val = ('BOLETIM' in solicitacao.tipo_documento.upper() or 'APROVEITAMENTO' in solicitacao.tipo_documento.upper())
    print(f"Should fetch grades? {val}")
    
    if val:
        print("Fetching grades...")
        notas = AcademicService.get_boletim_aluno(aluno, classe)
        print("Grades fetched successfully!")
        for n in notas:
            print(n['disciplina'], n['media_final'])
    else:
        print("Skipping grade fetch (not needed for this doc type).")

except Exception as e:
    print("\n!!! EXCEPTION CAUGHT IN GRADE CALC !!!")
    print(str(e))
    traceback.print_exc()
