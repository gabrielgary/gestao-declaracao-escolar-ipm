
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apis.models import Aluno, Turma, MatrizCurricular, Nota
from apis.services.academic_service import AcademicService
import json

def test_boletim():
    print("--- Iniciando Teste de Boletim ---")
    
    # 1. Buscar um aluno ativo
    aluno = Aluno.objects.filter(status_aluno='Activo').first()
    if not aluno:
        print("ERRO: Nenhum aluno ativo encontrado.")
        return

    print(f"Aluno Encontrado: {aluno.nome_completo} (ID: {aluno.id_aluno})")
    print(f"Turma: {aluno.id_turma.codigo_turma if aluno.id_turma else 'Sem Turma'}")

    # 2. Verificar se existe Matriz para a turma
    if aluno.id_turma:
        matriz = MatrizCurricular.objects.filter(
            id_curso=aluno.id_turma.id_curso,
            id_classe=aluno.id_turma.id_classe,
            ativo=True
        ).first()
        print(f"Matriz Curricular Encontrada: {'SIM' if matriz else 'NÃO'}")
    
    # 3. Testar o Serviço
    print("Calculando notas via AcademicService...")
    notas = AcademicService.get_boletim_aluno(aluno)
    
    # 4. Exibir Resultados
    print(f"Itens no Boletim: {len(notas)}")
    if len(notas) > 0:
        print(json.dumps(notas[0], indent=2, ensure_ascii=False)) # Mostra só a primeira disciplina
    else:
        print("AVISO: Boletim retornou vazio. Possíveis causas:")
        print(" - Falta de Matriz Curricular ativa")
        print(" - Falta de Disciplinas na Matriz")
        print(" - Matriz não corresponde ao Curso/Classe do aluno")

if __name__ == '__main__':
    test_boletim()
