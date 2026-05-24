
import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apis.models import Aluno, Turma, Nota

def verify():
    print("🔍 Verificando Dados no Banco...")
    
    # Verificar Turmas
    turmas = Turma.objects.filter(codigo_turma__in=['INF10A26', 'INF11A26'])
    print(f"\n🏫 Turmas Encontradas: {turmas.count()}")
    for t in turmas:
        qtd_alunos = Aluno.objects.filter(id_turma=t).count()
        print(f"   - {t.codigo_turma}: {qtd_alunos} alunos")

    # Verificar Alunos Totais de Teste
    alunos_teste = Aluno.objects.filter(numero_bi__contains='TESTE2026')
    print(f"\n👨‍🎓 Alunos de Teste (Total): {alunos_teste.count()}")
    
    # Verificar Notas
    if alunos_teste.exists():
        notas_total = Nota.objects.filter(id_aluno__in=alunos_teste).count()
        print(f"\n📝 Total de Notas Lançadas: {notas_total}")
        
        # Detalhe do primeiro aluno
        primeiro = alunos_teste.first()
        notas_primeiro = Nota.objects.filter(id_aluno=primeiro).count()
        print(f"   (Ex: Aluno '{primeiro.nome_completo}' tem {notas_primeiro} notas lançadas)")

if __name__ == "__main__":
    verify()
