import os
import django
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from apis.models import Aluno, Nota, SolicitacaoDocumento

def debug_grades():
    # Pegar uma solicitacao recente ou um aluno especifico
    solicitacao = SolicitacaoDocumento.objects.last()
    if not solicitacao:
        print("Nenhuma solicitacao encontrada.")
        return

    aluno = solicitacao.id_aluno
    print(f"--- Debugging Notas para Aluno: {aluno.nome_completo} (ID: {aluno.id_aluno}) ---")
    
    # Listar todas as notas deste aluno
    notas = Nota.objects.filter(id_aluno=aluno)
    print(f"Total de notas encontradas: {notas.count()}")
    
    if notas.exists():
        print(f"{'Disciplina':<30} | {'Trimestre':<15} | {'Tipo':<10} | {'Valor':<5}")
        print("-" * 70)
        for n in notas:
            disc_nome = n.id_disciplina.nome if n.id_disciplina else "N/A"
            print(f"{disc_nome:<30} | '{n.trimestre}' | '{n.tipo_nota}' | {n.valor}")
    else:
        print("SEM NOTAS NO BANCO DE DADOS PARA ESTE ALUNO.")

    # Testar logica do Service
    from apis.services.academic_service import AcademicService
    print("\n--- Testando AcademicService.get_boletim_aluno ---")
    resultados = AcademicService.get_boletim_aluno(aluno)
    for res in resultados:
        print(f"Disc: {res['disciplina']} | Media Final: {res['media_final']}")
        print(f"   Trimestres: {res['trimestres']}")

if __name__ == "__main__":
    debug_grades()
