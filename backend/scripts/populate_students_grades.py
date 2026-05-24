
import os
import sys
import django
import random
from decimal import Decimal

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apis.models import (
    Aluno, Turma, Classe, Curso, Periodo, Sala, 
    Disciplina, MatrizCurricular, MatrizCurricularDisciplina, 
    Nota, TipoDisciplina, Funcionario
)

def populate():
    print("🚀 Iniciando População de Dados de Teste (12 Alunos, 10ª/11ª Classe)...")

    # 1. Estrutura Base
    print("\n[1] Verificando/Criando Estrutura Base...")
    #sala, _ = Sala.objects.get_or_create(numero_sala="101", defaults={'capacidade_de_alunos': 30, 'localizacao': 'Bloco A'})
    sala, _ = Sala.objects.get_or_create(numero_sala="101", defaults={'capacidade_alunos': 30})
    periodo, _ = Periodo.objects.get_or_create(periodo="Manhã", defaults={'horario_inicio': '07:00:00', 'horario_fim': '12:00:00'})
    
    # Curso
    area_id = None # Simplificando, opcional
    curso, _ = Curso.objects.get_or_create(nome_curso="Informática", defaults={ 'duracao': 4})
    
    # Classes
    classe_10, _ = Classe.objects.get_or_create(nivel=10)#, #defaults={'descricao': 'Décima Classe'})
    classe_11, _ = Classe.objects.get_or_create(nivel=11)#, defaults={'descricao': 'Décima Primeira Classe'})

    # Tipo Disciplina
    tipo_disc, _ = TipoDisciplina.objects.get_or_create(nome_tipo="Nuclear", defaults={'sigla': 'NUC'})

    # Disciplinas
    disciplinas_nomes = ['Matemática', 'Física', 'Língua Portuguesa']
    disciplinas_objs = []
    for nome in disciplinas_nomes:
        disc, _ = Disciplina.objects.get_or_create(nome=nome, defaults={'id_tipo_disciplina': tipo_disc})
        disciplinas_objs.append(disc)

    # 2. Matrizes Curriculares (Importante para o DocumentService saber as disciplinas)
    print("\n[2] Configurando Matrizes Curriculares...")
    
    for cls in [classe_10, classe_11]:
        matriz, created = MatrizCurricular.objects.get_or_create(
            id_curso=curso,
            id_classe=cls,
            ano_letivo='2026',
            defaults={'descricao': f'Matriz {cls.nivel}ª Classe 2026', 'ativo': True}
        )
        
        # Associar disciplinas à matriz
        for disc in disciplinas_objs:
            MatrizCurricularDisciplina.objects.get_or_create(
                id_matriz_curricular=matriz,
                id_disciplina=disc,
                defaults={'carga_horaria': 4, 'coeficiente': 1.0, 'e_nuclear': True}
            )

    # 3. Turmas
    print("\n[3] Criando Turmas...")
    turma_10, _ = Turma.objects.get_or_create(
        codigo_turma="INF10A26",
        defaults={
            'id_classe': classe_10, 'id_curso': curso, 'id_periodo': periodo, 
            'id_sala': sala, 'ano': '2026'
        }
    )
    # Garantir Matriz na Turma
    matriz_10 = MatrizCurricular.objects.get(id_curso=curso, id_classe=classe_10, ano_letivo='2026')
    turma_10.id_matriz_curricular = matriz_10
    turma_10.save()

    turma_11, _ = Turma.objects.get_or_create(
        codigo_turma="INF11A26",
        defaults={
            'id_classe': classe_11, 'id_curso': curso, 'id_periodo': periodo, 
            'id_sala': sala, 'ano': '2026'
        }
    )
    matriz_11 = MatrizCurricular.objects.get(id_curso=curso, id_classe=classe_11, ano_letivo='2026')
    turma_11.id_matriz_curricular = matriz_11
    turma_11.save()

    # 4. Alunos e Notas
    print("\n[4] Criando Alunos e Lançando Notas...")
    
    # 6 Alunos na 10ª e 6 na 11ª
    turmas_target = [turma_10] * 6 + [turma_11] * 6
    
    trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre']
    tipos_nota = ['MAC', 'PP', 'PT']

    count = 1
    for turma_alvo in turmas_target:
        num_bi = f"00{count}TESTE2026"
        nome_aluno = f"Aluno Teste {count} - {turma_alvo.id_classe.nivel}ª"
        
        aluno, created = Aluno.objects.get_or_create(
            numero_bi=num_bi,
            defaults={
                'nome_completo': nome_aluno,
                'email': f"aluno{count}@teste.com",
                'id_turma': turma_alvo,
                'genero': 'M' if count % 2 == 0 else 'F',
               # 'estado_civil': 'Solteiro',
                'numero_matricula': f"MAT{count}2026"
            }
        )
        
        # Se já existia e estava em outra turma, atualiza
        if not created:
            aluno.id_turma = turma_alvo
            aluno.save()

        print(f"   > Processando {aluno.nome_completo} ({turma_alvo.codigo_turma})...")

        # Lançar Notas
        for trim in trimestres:
            for disc in disciplinas_objs:
                for t_nota in tipos_nota:
                    # Gerar nota aleatória entre 10 e 20
                    valor_nota = Decimal(random.randint(10, 20))
                    
                    Nota.objects.update_or_create(
                        id_aluno=aluno,
                        id_disciplina=disc,
                        id_turma=turma_alvo,
                        trimestre=trim,
                        tipo_nota=t_nota,
                        defaults={
                            'valor': valor_nota,
                            'tipo_avaliacao': 'Prova do Professor' if t_nota == 'PP' else 'Avaliação Continua' 
                        }
                    )
        count += 1
    
    # 5. GARANTIR NOTAS PARA SHELCIA DOMINGOS (Do Teste do Usuário)
    try:
        shelcia = Aluno.objects.filter(nome_completo__icontains="Shelcia").first()
        if shelcia:
            print(f"\n[5] Encontrada aluna teste: {shelcia.nome_completo}. Adicionando notas...")
            # Garantir que ela tenha turma/classe
            if not shelcia.id_turma:
                shelcia.id_turma = turma_11 # Assumindo 11 ou 12
                shelcia.save()
            
            for trim in trimestres:
                for disc in disciplinas_objs:
                    for t_nota in tipos_nota:
                        Nota.objects.update_or_create(
                            id_aluno=shelcia,
                            id_disciplina=disc,
                            id_turma=shelcia.id_turma,
                            trimestre=trim,
                            tipo_nota=t_nota,
                            defaults={'valor': Decimal(random.randint(12, 18))}
                        )
            print("   Notas adicionadas para Shelcia.")
    except Exception as e:
        print(f"   Erro ao processar Shelcia: {e}")

    print("\n✅ População Concluída com Sucesso!")
    print("   Total de Alunos: 12")
    print("   Turmas: INF10A26 e INF11A26")
    print("   Notas lançadas para 3 trimestres em Matemática, Física e Português.")

if __name__ == "__main__":
    populate()
