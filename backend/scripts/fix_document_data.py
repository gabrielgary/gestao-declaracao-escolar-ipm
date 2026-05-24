#!/usr/bin/env python
"""
Script de Correção de Dados Críticos para Geração de Documentos
Este script corrige problemas comuns nos dados de notas que impedem a geração de documentos
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Nota, Aluno, Disciplina, Turma, Classe, Curso, MatrizCurricular, MatrizCurricularDisciplina

class DataFixer:
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
        
    def run_all_fixes(self):
        """Executa todas as correções necessárias"""
        print("=" * 80)
        print("🔧 CORREÇÃO DE DADOS - SISTEMA DE DOCUMENTOS")
        print("=" * 80)
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # 1. Corrigir notas sem tipo
        self.fix_missing_tipo_nota()
        
        # 2. Corrigir notas sem trimestre
        self.fix_missing_trimestre()
        
        # 3. Corrigir notas sem disciplina
        self.fix_missing_disciplina()
        
        # 4. Corrigir notas sem turma
        self.fix_missing_turma()
        
        # 5. Criar matriz curricular padrão se não existir
        self.create_default_matrix()
        
        # 6. Validar valores das notas
        self.validate_grade_values()
        
        # 7. Resumo das correções
        self.generate_summary()
        
    def fix_missing_tipo_nota(self):
        """Corrige notas sem tipo_nota definido"""
        print("📝 1. CORRIGINDO NOTAS SEM TIPO")
        print("-" * 50)
        
        notas_sem_tipo = Nota.objects.filter(tipo_nota__isnull=True)
        count = notas_sem_tipo.count()
        
        print(f"Notas sem tipo_nota: {count}")
        
        if count > 0:
            # Estratégia: Classificar baseado na descrição da avaliação
            for nota in notas_sem_tipo:
                tipo_avaliacao = nota.tipo_avaliacao or ""
                
                # Lógica de classificação
                if "continua" in tipo_avaliacao.lower():
                    nota.tipo_nota = "MAC"
                elif "professor" in tipo_avaliacao.lower():
                    nota.tipo_nota = "PP"
                elif "trimestral" in tipo_avaliacao.lower():
                    nota.tipo_nota = "PT"
                else:
                    # Default para MAC se não conseguir classificar
                    nota.tipo_nota = "MAC"
                    
                nota.save()
                
            self.fixes_applied.append(f"Corrigidos {count} registros de tipo_nota")
            print(f"✅ {count} notas classificadas com sucesso")
        else:
            print("✅ Todas as notas já têm tipo definido")
            
        print()
        
    def fix_missing_trimestre(self):
        """Corrige notas sem trimestre definido"""
        print("📅 2. CORRIGINDO NOTAS SEM TRIMESTRE")
        print("-" * 50)
        
        notas_sem_trimestre = Nota.objects.filter(trimestre__isnull=True)
        count = notas_sem_trimestre.count()
        
        print(f"Notas sem trimestre: {count}")
        
        if count > 0:
            # Estratégia: Definir trimestre baseado na data de lançamento
            for nota in notas_sem_trimestre:
                data_lancamento = nota.data_lancamento
                
                if data_lancamento:
                    month = data_lancamento.month
                    
                    # Lógica simples baseada nos meses do ano
                    if month in [3, 4, 5]:  # Março, Abril, Maio
                        nota.trimestre = "1º Trimestre"
                    elif month in [6, 7, 8]:  # Junho, Julho, Agosto
                        nota.trimestre = "2º Trimestre"
                    elif month in [9, 10, 11, 12]:  # Setembro, Outubro, Novembro, Dezembro
                        nota.trimestre = "3º Trimestre"
                    else:  # Janeiro, Fevereiro
                        nota.trimestre = "1º Trimestre"
                else:
                    # Default para primeiro trimestre
                    nota.trimestre = "1º Trimestre"
                    
                nota.save()
                
            self.fixes_applied.append(f"Corrigidos {count} registros de trimestre")
            print(f"✅ {count} notas com trimestre definido")
        else:
            print("✅ Todas as notas já têm trimestre definido")
            
        print()
        
    def fix_missing_disciplina(self):
        """Tenta associar notas sem disciplina"""
        print("📚 3. CORRIGINDO NOTAS SEM DISCIPLINA")
        print("-" * 50)
        
        notas_sem_disciplina = Nota.objects.filter(id_disciplina__isnull=True)
        count = notas_sem_disciplina.count()
        
        print(f"Notas sem disciplina: {count}")
        
        if count > 0:
            # Estratégia: Tentar associar baseado no professor e turma
            disciplinas_disponiveis = Disciplina.objects.all()
            
            if disciplinas_disponiveis.exists():
                disciplina_default = disciplinas_disponiveis.first()
                
                for nota in notas_sem_disciplina:
                    # Tenta encontrar disciplina apropriada
                    if nota.id_professor and nota.id_turma:
                        # Buscar disciplinas que estejam associadas a este professor/turma
                        from apis.models import ProfessorDisciplina
                        prof_disc = ProfessorDisciplina.objects.filter(
                            id_funcionario=nota.id_professor,
                            id_turma=nota.id_turma
                        ).first()
                        
                        if prof_disc:
                            nota.id_disciplina = prof_disc.id_disciplina
                        else:
                            # Usa a primeira disciplina disponível
                            nota.id_disciplina = disciplina_default
                    else:
                        # Usa a primeira disciplina disponível
                        nota.id_disciplina = disciplina_default
                        
                    nota.save()
                    
                self.fixes_applied.append(f"Associadas {count} notas a disciplinas")
                print(f"✅ {count} notas associadas a disciplinas")
            else:
                print("❌ Nenhuma disciplina disponível para associar")
                self.errors.append("Não existem disciplinas cadastradas")
        else:
            print("✅ Todas as notas já têm disciplina associada")
            
        print()
        
    def fix_missing_turma(self):
        """Tenta associar alunos sem turma"""
        print("👥 4. CORRIGINDO ALUNOS SEM TURMA")
        print("-" * 50)
        
        alunos_sem_turma = Aluno.objects.filter(id_turma__isnull=True)
        count = alunos_sem_turma.count()
        
        print(f"Alunos sem turma: {count}")
        
        if count > 0:
            # Verificar se há turmas disponíveis
            turmas_disponiveis = Turma.objects.all()
            
            if turmas_disponiveis.exists():
                turma_default = turmas_disponiveis.first()
                
                for aluno in alunos_sem_turma:
                    # Associar à primeira turma disponível
                    aluno.id_turma = turma_default
                    aluno.save()
                    
                self.fixes_applied.append(f"Associados {count} alunos a turmas")
                print(f"✅ {count} alunos associados à turma padrão")
            else:
                print("❌ Nenhuma turma disponível para associar")
                self.errors.append("Não existem turmas cadastradas")
        else:
            print("✅ Todos os alunos já têm turma associada")
            
        print()
        
    def create_default_matrix(self):
        """Cria matriz curricular padrão se não existir"""
        print("📋 5. CRIANDO MATRIZ CURRICULAR PADRÃO")
        print("-" * 50)
        
        # Verificar se já existe matriz
        matrizes_existentes = MatrizCurricular.objects.count()
        print(f"Matrizes existentes: {matrizes_existentes}")
        
        if matrizes_existentes == 0:
            # Criar matriz curricular padrão
            cursos = Curso.objects.all()
            classes = Classe.objects.all()
            
            if cursos.exists() and classes.exists():
                curso_default = cursos.first()
                
                for classe in classes:
                    matriz = MatrizCurricular.objects.create(
                        id_curso=curso_default,
                        id_classe=classe,
                        ativo=True,
                        descricao=f"Matriz Curricular - {classe.nivel}ª Classe"
                    )
                    
                    # Associar todas as disciplinas à matriz
                    disciplinas = Disciplina.objects.all()
                    for disciplina in disciplinas:
                        MatrizCurricularDisciplina.objects.create(
                            id_matriz_curricular=matriz,
                            id_disciplina=disciplina,
                            coeficiente=1.0
                        )
                        
                    print(f"✅ Criada matriz para {classe.nivel}ª classe com {disciplinas.count()} disciplinas")
                    
                self.fixes_applied.append("Criada matriz curricular padrão")
            else:
                print("❌ Cursos ou classes não encontrados")
                self.errors.append("Não é possível criar matriz sem cursos/classes")
        else:
            print("✅ Matrizes curriculares já existem")
            
        print()
        
    def validate_grade_values(self):
        """Valida e corrige valores das notas"""
        print("🔍 6. VALIDANDO VALORES DAS NOTAS")
        print("-" * 50)
        
        # Notas fora do intervalo
        notas_invalidas = Nota.objects.filter(valor__lt=0) | Nota.objects.filter(valor__gt=20)
        count = notas_invalidas.count()
        
        print(f"Notas fora do intervalo (0-20): {count}")
        
        if count > 0:
            for nota in notas_invalidas:
                if nota.valor < 0:
                    nota.valor = 0
                elif nota.valor > 20:
                    nota.valor = 20
                nota.save()
                
            self.fixes_applied.append(f"Corrigidos {count} valores de notas")
            print(f"✅ {count} valores de notas corrigidos")
        else:
            print("✅ Todas as notas têm valores válidos")
            
        print()
        
    def generate_summary(self):
        """Gera resumo das correções"""
        print("📊 7. RESUMO DAS CORREÇÕES")
        print("-" * 50)
        
        print(f"\n✅ CORREÇÕES APLICADAS: {len(self.fixes_applied)}")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
            
        if self.errors:
            print(f"\n❌ ERROS ENCONTRADOS: {len(self.errors)}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
                
        print(f"\n📈 ESTATÍSTICAS FINAIS:")
        print(f"  Total de notas: {Nota.objects.count()}")
        print(f"  Notas com tipo: {Nota.objects.filter(tipo_nota__isnull=False).count()}")
        print(f"  Notas com trimestre: {Nota.objects.filter(trimestre__isnull=False).count()}")
        print(f"  Notas com disciplina: {Nota.objects.filter(id_disciplina__isnull=False).count()}")
        print(f"  Alunos com turma: {Aluno.objects.filter(id_turma__isnull=False).count()}")
        
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print("  1. Testar a geração de documentos")
        print("  2. Verificar se os boletins agora mostram as notas")
        print("  3. Validar declarações e certificados")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    fixer = DataFixer()
    fixer.run_all_fixes()
