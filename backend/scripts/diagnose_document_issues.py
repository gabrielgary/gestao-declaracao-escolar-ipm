#!/usr/bin/env python
"""
Script de Diagnóstico Avançado para Problemas de Notas em Documentos
Este script identifica problemas nos dados que impedem a geração correta de boletins e declarações
"""

import os
import sys
import django
from datetime import datetime
from collections import defaultdict

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Nota, Aluno, Disciplina, Turma, Classe, Curso, MatrizCurricular, MatrizCurricularDisciplina
from apis.services.academic_service import AcademicService

class DocumentDiagnostic:
    def __init__(self):
        self.issues = []
        self.stats = defaultdict(int)
        
    def run_full_diagnosis(self):
        """Executa diagnóstico completo"""
        print("=" * 80)
        print("🔍 DIAGNÓSTICO AVANÇADO - SISTEMA DE DOCUMENTOS")
        print("=" * 80)
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # 1. Verificar estrutura básica
        self.check_basic_structure()
        
        # 2. Analisar qualidade dos dados de notas
        self.analyze_grades_data()
        
        # 3. Verificar relacionamentos
        self.check_relationships()
        
        # 4. Testar serviço acadêmico
        self.test_academic_service()
        
        # 5. Verificar matriz curricular
        self.check_curriculum_matrix()
        
        # 6. Resumo e recomendações
        self.generate_summary()
        
    def check_basic_structure(self):
        """Verifica estrutura básica do banco de dados"""
        print("📊 1. ESTRUTURA BÁSICA DE DADOS")
        print("-" * 50)
        
        self.stats['total_alunos'] = Aluno.objects.count()
        self.stats['total_notas'] = Nota.objects.count()
        self.stats['total_disciplinas'] = Disciplina.objects.count()
        self.stats['total_turmas'] = Turma.objects.count()
        self.stats['total_classes'] = Classe.objects.count()
        self.stats['total_cursos'] = Curso.objects.count()
        
        print(f"Alunos cadastrados: {self.stats['total_alunos']}")
        print(f"Notas registradas: {self.stats['total_notas']}")
        print(f"Disciplinas: {self.stats['total_disciplinas']}")
        print(f"Turmas: {self.stats['total_turmas']}")
        print(f"Classes: {self.stats['total_classes']}")
        print(f"Cursos: {self.stats['total_cursos']}")
        
        if self.stats['total_notas'] == 0:
            self.issues.append("CRÍTICO: Nenhuma nota encontrada no sistema!")
        elif self.stats['total_alunos'] == 0:
            self.issues.append("CRÍTICO: Nenhum aluno encontrado no sistema!")
            
        print()
        
    def analyze_grades_data(self):
        """Analisa qualidade dos dados de notas"""
        print("📝 2. ANÁLISE DE QUALIDADE DAS NOTAS")
        print("-" * 50)
        
        # Verificar campos nulos críticos
        notas_sem_disciplina = Nota.objects.filter(id_disciplina__isnull=True).count()
        notas_sem_tipo = Nota.objects.filter(tipo_nota__isnull=True).count()
        notas_sem_trimestre = Nota.objects.filter(trimestre__isnull=True).count()
        notas_sem_turma = Nota.objects.filter(id_turma__isnull=True).count()
        
        print(f"Notas sem disciplina: {notas_sem_disciplina}")
        print(f"Notas sem tipo_nota: {notas_sem_tipo}")
        print(f"Notas sem trimestre: {notas_sem_trimestre}")
        print(f"Notas sem turma: {notas_sem_turma}")
        
        # Análise por tipo de nota
        print("\nDistribuição por tipo de nota:")
        for tipo in ['MAC', 'PP', 'PT']:
            count = Nota.objects.filter(tipo_nota=tipo).count()
            print(f"  {tipo}: {count}")
            self.stats[f'notas_{tipo.lower()}'] = count
            
        # Análise por trimestre
        print("\nDistribuição por trimestre:")
        for trim in ['1º Trimestre', '2º Trimestre', '3º Trimestre']:
            count = Nota.objects.filter(trimestre=trim).count()
            print(f"  {trim}: {count}")
            
        # Verificar valores inválidos
        notas_fora_intervalo = Nota.objects.filter(valor__lt=0).count() + Nota.objects.filter(valor__gt=20).count()
        if notas_fora_intervalo > 0:
            print(f"\n⚠️  Notas fora do intervalo 0-20: {notas_fora_intervalo}")
            self.issues.append(f"{notas_fora_intervalo} notas fora do intervalo válido (0-20)")
            
        # Registrar problemas
        if notas_sem_disciplina > 0:
            self.issues.append(f"{notas_sem_disciplina} notas sem disciplina associada")
        if notas_sem_tipo > 0:
            self.issues.append(f"{notas_sem_tipo} notas sem tipo definido (MAC/PP/PT)")
        if notas_sem_trimestre > 0:
            self.issues.append(f"{notas_sem_trimestre} notas sem trimestre definido")
            
        print()
        
    def check_relationships(self):
        """Verifica integridade dos relacionamentos"""
        print("🔗 3. VERIFICAÇÃO DE RELACIONAMENTOS")
        print("-" * 50)
        
        # Alunos sem turma
        alunos_sem_turma = Aluno.objects.filter(id_turma__isnull=True).count()
        print(f"Alunos sem turma: {alunos_sem_turma}")
        
        # Alunos com notas mas sem turma
        alunos_com_notas_sem_turma = Aluno.objects.filter(
            nota__isnull=False,
            id_turma__isnull=True
        ).distinct().count()
        print(f"Alunos com notas mas sem turma: {alunos_com_notas_sem_turma}")
        
        # Turmas sem alunos
        turmas_sem_alunos = Turma.objects.filter(aluno__isnull=True).count()
        print(f"Turmas sem alunos: {turmas_sem_alunos}")
        
        # Disciplinas sem notas
        disciplinas_sem_notas = Disciplina.objects.filter(nota__isnull=True).count()
        print(f"Disciplinas sem notas: {disciplinas_sem_notas}")
        
        if alunos_com_notas_sem_turma > 0:
            self.issues.append(f"{alunos_com_notas_sem_turma} alunos têm notas mas não estão associados a turma")
            
        print()
        
    def test_academic_service(self):
        """Testa o serviço acadêmico com alunos reais"""
        print("🧪 4. TESTE DO SERVIÇO ACADÊMICO")
        print("-" * 50)
        
        # Pegar alguns alunos para teste
        alunos_teste = Aluno.objects.filter(nota__isnull=False).distinct()[:3]
        
        if not alunos_teste:
            print("❌ Nenhum aluno com notas encontrado para teste")
            self.issues.append("Não há alunos com notas para testar o serviço")
            return
            
        for i, aluno in enumerate(alunos_teste, 1):
            print(f"\nTeste {i}: {aluno.nome_completo} (ID: {aluno.id_aluno})")
            
            try:
                # Testar get_boletim_aluno
                boletim = AcademicService.get_boletim_aluno(aluno)
                
                if boletim:
                    print(f"  ✅ Boletim gerado com {len(boletim)} disciplinas")
                    
                    # Verificar primeira disciplina
                    if boletim[0]:
                        primeira = boletim[0]
                        print(f"  📚 Primeira disciplina: {primeira.get('disciplina', 'N/A')}")
                        print(f"  📊 Média final: {primeira.get('media_final', 'N/A')}")
                        print(f"  📈 Trimestres com dados: {primeira.get('count_mt', 0)}")
                        
                        # Verificar estrutura dos trimestres
                        trimestres = primeira.get('trimestres', {})
                        for trim_num, trim_data in trimestres.items():
                            notas_trim = [v for v in trim_data.values() if v is not None]
                            if notas_trim:
                                print(f"    Trimestre {trim_num}: {len(notas_trim)} notas ({trim_data})")
                else:
                    print("  ❌ Boletim retornou vazio")
                    self.issues.append(f"Boletim vazio para aluno {aluno.nome_completo}")
                    
            except Exception as e:
                print(f"  ❌ Erro ao gerar boletim: {str(e)}")
                self.issues.append(f"Erro no serviço acadêmico para {aluno.nome_completo}: {str(e)}")
                
        print()
        
    def check_curriculum_matrix(self):
        """Verifica matriz curricular"""
        print("📋 5. VERIFICAÇÃO DE MATRIZ CURRICULAR")
        print("-" * 50)
        
        total_matrizes = MatrizCurricular.objects.count()
        print(f"Matrizes curriculares: {total_matrizes}")
        
        if total_matrizes == 0:
            print("❌ Nenhuma matriz curricular encontrada")
            self.issues.append("Não existem matrizes curriculares cadastradas")
            return
            
        # Verificar matrizes por curso/classe
        matrizes_ativas = MatrizCurricular.objects.filter(ativo=True).count()
        print(f"Matrizes ativas: {matrizes_ativas}")
        
        # Disciplinas nas matrizes
        total_disciplinas_matriz = MatrizCurricularDisciplina.objects.count()
        print(f"Disciplinas nas matrizes: {total_disciplinas_matriz}")
        
        if total_disciplinas_matriz == 0:
            self.issues.append("Nenhuma disciplina associada às matrizes curriculares")
            
        print()
        
    def generate_summary(self):
        """Gera resumo e recomendações"""
        print("📋 6. RESUMO E RECOMENDAÇÕES")
        print("-" * 50)
        
        print(f"\n📊 ESTATÍSTICAS:")
        for key, value in self.stats.items():
            print(f"  {key}: {value}")
            
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS ({len(self.issues)}):")
        
        if not self.issues:
            print("  ✅ Nenhum problema crítico encontrado!")
        else:
            for i, issue in enumerate(self.issues, 1):
                severity = "🔴 CRÍTICO" if "CRÍTICO" in issue else "⚠️  AVISO"
                print(f"  {i}. [{severity}] {issue}")
                
        print(f"\n🛠️  RECOMENDAÇÕES:")
        
        if self.stats['total_notas'] == 0:
            print("  1. IMPORTAR: Importar notas dos alunos para o sistema")
            
        if any("sem tipo" in issue.lower() for issue in self.issues):
            print("  2. CORRIGIR: Executar script para classificar tipos de notas (MAC/PP/PT)")
            
        if any("sem trimestre" in issue.lower() for issue in self.issues):
            print("  3. CORRIGIR: Executar script para definir trimestres das notas")
            
        if any("sem disciplina" in issue.lower() for issue in self.issues):
            print("  4. ASSOCIAR: Vincular notas às disciplinas correspondentes")
            
        if any("matriz" in issue.lower() for issue in self.issues):
            print("  5. CONFIGURAR: Criar matrizes curriculares para cursos e classes")
            
        if any("sem turma" in issue.lower() for issue in self.issues):
            print("  6. ORGANIZAR: Associar alunos às turmas corretas")
            
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("  1. Executar os scripts de correção sugeridos")
        print("  2. Testar novamente a geração de documentos")
        print("  3. Validar com usuários do sistema")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    diagnostic = DocumentDiagnostic()
    diagnostic.run_full_diagnosis()
