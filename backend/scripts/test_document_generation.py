#!/usr/bin/env python
"""
Script de Teste para Geração de Documentos
Este script testa a geração de documentos após as correções
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Aluno, Nota, SolicitacaoDocumento
from apis.services.academic_service import AcademicService
from apis.services.document_service import DocumentService

class DocumentTester:
    def __init__(self):
        self.test_results = []
        self.errors = []
        
    def run_all_tests(self):
        """Executa todos os testes"""
        print("=" * 80)
        print("🧪 TESTE DE GERAÇÃO DE DOCUMENTOS")
        print("=" * 80)
        print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # 1. Testar validação de dados
        self.test_data_validation()
        
        # 2. Testar serviço acadêmico
        self.test_academic_service()
        
        # 3. Testar geração de boletim
        self.test_boletim_generation()
        
        # 4. Testar geração de documentos
        self.test_document_generation()
        
        # 5. Relatório final
        self.generate_test_report()
        
    def test_data_validation(self):
        """Testa validação dos dados"""
        print("📊 1. TESTE DE VALIDAÇÃO DE DADOS")
        print("-" * 50)
        
        try:
            problemas = AcademicService.validar_dados_notas()
            
            if problemas:
                print(f"❌ {len(problemas)} problemas encontrados:")
                for problema in problemas:
                    print(f"  - {problema}")
                    self.errors.append(f"Validação: {problema}")
            else:
                print("✅ Nenhum problema de validação encontrado")
                self.test_results.append("Validação de dados: OK")
                
        except Exception as e:
            print(f"❌ Erro na validação: {str(e)}")
            self.errors.append(f"Erro validação: {str(e)}")
            
        print()
        
    def test_academic_service(self):
        """Testa o serviço acadêmico"""
        print("🎓 2. TESTE DO SERVIÇO ACADÊMICO")
        print("-" * 50)
        
        # Pegar alguns alunos para teste
        alunos_teste = Aluno.objects.all()[:3]
        
        if not alunos_teste:
            print("❌ Nenhum aluno encontrado para teste")
            self.errors.append("Nenhum aluno encontrado")
            return
            
        for i, aluno in enumerate(alunos_teste, 1):
            print(f"\nTeste {i}: {aluno.nome_completo}")
            
            try:
                # Testar resumo acadêmico
                resumo = AcademicService.obter_resumo_academico(aluno.id_aluno)
                if resumo:
                    print(f"  ✅ Resumo acadêmico gerado")
                    print(f"     Média geral: {resumo.get('media_geral', 'N/A')}")
                    print(f"     Total faltas: {resumo.get('total_faltas', 'N/A')}")
                    self.test_results.append(f"Resumo acadêmico {aluno.nome_completo}: OK")
                else:
                    print(f"  ❌ Falha ao gerar resumo acadêmico")
                    self.errors.append(f"Resumo acadêmico falhou para {aluno.nome_completo}")
                    
            except Exception as e:
                print(f"  ❌ Erro: {str(e)}")
                self.errors.append(f"Erro serviço acadêmico {aluno.nome_completo}: {str(e)}")
                
        print()
        
    def test_boletim_generation(self):
        """Testa geração de boletim"""
        print("📋 3. TESTE DE GERAÇÃO DE BOLETIM")
        print("-" * 50)
        
        # Pegar um aluno que tenha notas
        aluno_com_notas = Aluno.objects.filter(nota__isnull=False).distinct().first()
        
        if not aluno_com_notas:
            print("❌ Nenhum aluno com notas encontrado")
            self.errors.append("Nenhum aluno com notas para testar boletim")
            return
            
        print(f"Testando boletim para: {aluno_com_notas.nome_completo}")
        
        try:
            boletim = AcademicService.get_boletim_aluno(aluno_com_notas)
            
            if boletim:
                print(f"✅ Boletim gerado com {len(boletim)} disciplinas")
                
                # Detalhar primeira disciplina
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
                            print(f"    Trimestre {trim_num}: {len(notas_trim)} notas")
                            
                self.test_results.append(f"Boletim {aluno_com_notas.nome_completo}: OK")
            else:
                print("❌ Boletim retornou vazio")
                self.errors.append(f"Boletim vazio para {aluno_com_notas.nome_completo}")
                
        except Exception as e:
            print(f"❌ Erro ao gerar boletim: {str(e)}")
            self.errors.append(f"Erro boletim {aluno_com_notas.nome_completo}: {str(e)}")
            
        print()
        
    def test_document_generation(self):
        """Testa geração de documentos"""
        print("📄 4. TESTE DE GERAÇÃO DE DOCUMENTOS")
        print("-" * 50)
        
        # Verificar se há solicitações para testar
        solicitacoes = SolicitacaoDocumento.objects.filter(
            status_solicitacao='pago'
        )[:3]
        
        if not solicitacoes:
            print("⚠️  Nenhuma solicitação paga encontrada para teste")
            print("   Criando solicitação de teste...")
            
            # Tentar criar uma solicitação de teste
            try:
                aluno_teste = Aluno.objects.first()
                if aluno_teste:
                    solicitacao, fatura = DocumentService.criar_solicitacao(
                        aluno_teste.id_aluno,
                        "BOLETIM_1",
                        "fisico_rup"
                    )
                    print(f"✅ Solicitação de teste criada: {solicitacao.id_solicitacao}")
                    solicitacoes = [solicitacao]
                else:
                    print("❌ Nenhum aluno encontrado para criar solicitação")
                    return
            except Exception as e:
                print(f"❌ Erro ao criar solicitação de teste: {str(e)}")
                return
                
        for solicitacao in solicitacoes:
            print(f"\nTestando documento: {solicitacao.tipo_documento}")
            print(f"Aluno: {solicitacao.id_aluno.nome_completo}")
            
            try:
                # Tentar gerar PDF
                caminho_pdf = DocumentService.gerar_pdf_documento(
                    solicitacao.id_solicitacao,
                    solicitacao.id_funcionario.id_funcionario if solicitacao.id_funcionario else None
                )
                
                if caminho_pdf:
                    print(f"✅ PDF gerado: {caminho_pdf}")
                    self.test_results.append(f"Documento {solicitacao.tipo_documento}: OK")
                else:
                    print("❌ Falha ao gerar PDF")
                    self.errors.append(f"Falha PDF {solicitacao.tipo_documento}")
                    
            except Exception as e:
                print(f"❌ Erro ao gerar documento: {str(e)}")
                self.errors.append(f"Erro documento {solicitacao.tipo_documento}: {str(e)}")
                
        print()
        
    def generate_test_report(self):
        """Gera relatório final dos testes"""
        print("📊 5. RELATÓRIO FINAL DE TESTES")
        print("-" * 50)
        
        print(f"\n✅ TESTES BEM-SUCEDIDOS: {len(self.test_results)}")
        for result in self.test_results:
            print(f"  ✓ {result}")
            
        if self.errors:
            print(f"\n❌ ERROS ENCONTRADOS: {len(self.errors)}")
            for error in self.errors:
                print(f"  ✗ {error}")
                
        # Verificação final
        total_tests = len(self.test_results) + len(self.errors)
        success_rate = (len(self.test_results) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 TAXA DE SUCESSO: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 SISTEMA FUNCIONANDO BEM!")
            print("   Os documentos devem estar gerando corretamente.")
        elif success_rate >= 60:
            print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
            print("   Alguns problemas precisam ser resolvidos.")
        else:
            print("🚨 SISTEMA COM PROBLEMAS CRÍTICOS")
            print("   É necessário investigar e corrigir os erros.")
            
        print("\n🚀 RECOMENDAÇÕES:")
        if success_rate < 100:
            print("  1. Corrigir os erros identificados")
            print("  2. Executar novamente os testes")
            print("  3. Validar com usuários reais")
        else:
            print("  1. Monitorar o sistema em produção")
            print("  2. Coletar feedback dos usuários")
            print("  3. Implementar melhorias contínuas")
            
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = DocumentTester()
    tester.run_all_tests()
