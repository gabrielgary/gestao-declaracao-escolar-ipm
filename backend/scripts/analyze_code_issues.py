#!/usr/bin/env python
"""
Análise Estática do Código - Identificação de Problemas na Geração de Documentos
Este script analisa o código-fonte para identificar problemas potenciais
"""

import os
import re
from pathlib import Path

class CodeAnalyzer:
    def __init__(self):
        self.backend_path = Path(__file__).parent
        self.issues = []
        self.recommendations = []
        
    def analyze_academic_service(self):
        """Analisa o academic_service.py em busca de problemas"""
        print("🔍 ANÁLISE DO ACADEMIC_SERVICE.PY")
        print("=" * 60)
        
        service_path = self.backend_path / 'apis' / 'services' / 'academic_service.py'
        
        if not service_path.exists():
            self.issues.append("CRÍTICO: academic_service.py não encontrado")
            return
            
        with open(service_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar problemas potenciais
        issues_found = []
        
        # 1. Verificar tratamento de nulos
        if 'id_disciplina__isnull=True' not in content:
            issues_found.append("Não há filtro para disciplinas nulas")
            
        # 2. Verificar fallbacks complexos
        if 'Prioridade' in content:
            fallback_count = content.count('Prioridade')
            if fallback_count > 3:
                issues_found.append(f"Muitos fallbacks ({fallback_count}) - pode causar confusão")
                
        # 3. Verificar tratamento de exceções
        try_count = content.count('try:')
        except_count = content.count('except')
        if try_count != except_count:
            issues_found.append("Blocos try/except desbalanceados")
            
        # 4. Verificar consultas N+1
        if '.select_related(' not in content:
            issues_found.append("Possível problema N+1 - sem select_related")
            
        # 5. Verificar lógica de médias
        if 'media_final = 0.0' in content:
            issues_found.append("Média final sendo forçada para 0.0 em alguns casos")
            
        print("Problemas identificados:")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
            self.issues.append(f"academic_service.py: {issue}")
            
        # Recomendações
        if fallback_count > 2:
            self.recommendations.append("Simplificar lógica de fallbacks no academic_service.py")
        if '.select_related(' not in content:
            self.recommendations.append("Adicionar select_related para otimizar consultas")
            
        print()
        
    def analyze_document_service(self):
        """Analisa o document_service.py"""
        print("🔍 ANÁLISE DO DOCUMENT_SERVICE.PY")
        print("=" * 60)
        
        service_path = self.backend_path / 'apis' / 'services' / 'document_service.py'
        
        if not service_path.exists():
            self.issues.append("CRÍTICO: document_service.py não encontrado")
            return
            
        with open(service_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        issues_found = []
        
        # 1. Verificar chamada ao academic_service
        if 'AcademicService.get_boletim_aluno' in content:
            print("✅ Chamada correta ao AcademicService.get_boletim_aluno")
        else:
            issues_found.append("Não há chamada ao AcademicService para obter notas")
            
        # 2. Verificar tratamento de erro
        if 'except Exception as e:' in content:
            print("✅ Tratamento de exceções presente")
        else:
            issues_found.append("Falta tratamento de exceções na geração de PDF")
            
        # 3. Verificar validação de dados
        if 'notas_finais' in content:
            print("✅ Contexto notas_finais sendo preparado")
        else:
            issues_found.append("Contexto notas_finais não encontrado")
            
        # 4. Verificar templates
        templates = ['boletim.html', 'declaracao_aproveitamento.html', 'certificado.html']
        for template in templates:
            if template in content:
                print(f"✅ Template {template} referenciado")
            else:
                issues_found.append(f"Template {template} não referenciado")
                
        print("Problemas identificados:")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
            self.issues.append(f"document_service.py: {issue}")
            
        print()
        
    def analyze_templates(self):
        """Analisa os templates PDF"""
        print("🔍 ANÁLISE DOS TEMPLATES PDF")
        print("=" * 60)
        
        templates_dir = self.backend_path / 'templates' / 'pdf'
        
        if not templates_dir.exists():
            self.issues.append("CRÍTICO: Diretório templates/pdf não encontrado")
            return
            
        # Analisar boletim.html
        boletim_path = templates_dir / 'boletim.html'
        if boletim_path.exists():
            with open(boletim_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues_found = []
            
            # Verificar variáveis críticas
            critical_vars = ['notas_finais', 'aluno', 'trimestre_selecionado']
            for var in critical_vars:
                if f'{{{{ {var}' in content:
                    print(f"✅ Variável {var} encontrada no template")
                else:
                    issues_found.append(f"Variável {var} não encontrada no template")
                    
            # Verificar filtro custom
            if 'get_item:' in content:
                print("✅ Filtro custom get_item sendo usado")
            else:
                issues_found.append("Filtro custom get_item não encontrado")
                
            # Verificar tratamento de nulos
            if 'default_if_none' in content:
                print("✅ Tratamento de valores nulos presente")
            else:
                issues_found.append("Falta tratamento de valores nulos")
                
            print("Problemas no boletim.html:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue}")
                self.issues.append(f"boletim.html: {issue}")
        else:
            self.issues.append("CRÍTICO: boletim.html não encontrado")
            
        print()
        
    def analyze_models(self):
        """Analisa os modelos relacionados"""
        print("🔍 ANÁLISE DOS MODELOS")
        print("=" * 60)
        
        models_dir = self.backend_path / 'apis' / 'models'
        
        # Analisar modelo Nota
        nota_path = models_dir / 'avaliacoes.py'
        if nota_path.exists():
            with open(nota_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues_found = []
            
            # Verificar campos críticos
            if 'id_disciplina = models.ForeignKey' in content:
                print("✅ Campo id_disciplina definido")
            else:
                issues_found.append("Campo id_disciplina não encontrado")
                
            if 'tipo_nota = models.CharField' in content:
                print("✅ Campo tipo_nota definido")
            else:
                issues_found.append("Campo tipo_nota não encontrado")
                
            if 'trimestre = models.CharField' in content:
                print("✅ Campo trimestre definido")
            else:
                issues_found.append("Campo trimestre não encontrado")
                
            # Verificar se campos permitem nulo
            if 'null=True' in content and 'blank=True' in content:
                print("⚠️  Campos permitem valores nulos - pode causar problemas")
                issues_found.append("Campos críticos permitem nulos")
                
            print("Problemas no modelo Nota:")
            for i, issue in enumerate(issues_found, 1):
                print(f"  {i}. {issue}")
                self.issues.append(f"models.avaliacoes.py: {issue}")
                
        print()
        
    def generate_report(self):
        """Gera relatório final"""
        print("📋 RELATÓRIO FINAL")
        print("=" * 60)
        
        print(f"\n🚨 PROBLEMAS ENCONTRADOS: {len(self.issues)}")
        for i, issue in enumerate(self.issues, 1):
            print(f"  {i}. {issue}")
            
        print(f"\n💡 RECOMENDAÇÕES: {len(self.recommendations)}")
        for i, rec in enumerate(self.recommendations, 1):
            print(f"  {i}. {rec}")
            
        # Plano de ação
        print(f"\n🛠️  PLANO DE AÇÃO SUGERIDO:")
        
        if any("CRÍTICO" in issue for issue in self.issues):
            print("  1. 🔴 URGENTE: Corrigir problemas críticos identificados")
            
        if any("nulos" in issue.lower() for issue in self.issues):
            print("  2. 📝 Validar e corrigir dados nulos no banco")
            
        if any("template" in issue.lower() for issue in self.issues):
            print("  3. 🎨 Ajustar templates para lidar com dados ausentes")
            
        if any("fallback" in issue.lower() for issue in self.issues):
            print("  4. 🔧 Simplificar lógica de fallbacks")
            
        print("  5. 🧪 Testar geração de documentos após correções")
        print("  6. 📊 Implementar monitoramento para detectar problemas")
        
        print("\n" + "=" * 60)

def main():
    analyzer = CodeAnalyzer()
    
    print("ANÁLISE ESTÁTICA - PROBLEMAS NA GERAÇÃO DE DOCUMENTOS")
    print("=" * 80)
    print()
    
    analyzer.analyze_models()
    analyzer.analyze_academic_service()
    analyzer.analyze_document_service()
    analyzer.analyze_templates()
    analyzer.generate_report()

if __name__ == "__main__":
    main()
