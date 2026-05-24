import os
import sys
import django
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Funcionario
from rest_framework.test import APIClient
from django.contrib.auth.models import User

def test_reports():
    print("=" * 50)
    print("🚀 INICIANDO TESTE DE RELATÓRIOS")
    print("=" * 50)
    
    client = APIClient()
    
    # Criar ou obter um usuário para autenticação
    user, _ = User.objects.get_or_create(username='admin_test', is_staff=True)
    client.force_authenticate(user=user)
    
    endpoints = [
        ('/api/reports/solicitacoes/', 'Solicitações'),
        ('/api/reports/alunos/', 'Alunos'),
        ('/api/reports/funcionarios/', 'Funcionários'),
        ('/api/reports/mensal/', 'Relatório Mensal'),
        ('/api/reports/auditoria/', 'Auditoria (Histórico)'),
        ('/api/reports/auditoria/?tipo=login', 'Auditoria (Login)'),
    ]
    
    formats = ['csv', 'pdf']
    
    for endpoint, label in endpoints:
        print(f"\n📊 Testando: {label}")
        for fmt in formats:
            url = f"{endpoint}{'&' if '?' in endpoint else '?'}format={fmt}"
            response = client.get(url)
            
            if response.status_code == 200:
                content_type = response['Content-Type']
                size = len(response.content)
                print(f"  ✅ {fmt.upper()}: OK (Type: {content_type}, Size: {size} bytes)")
                
                # Verificações básicas de conteúdo
                if fmt == 'pdf':
                    if not response.content.startswith(b'%PDF'):
                        print(f"    ❌ Erro: Arquivo PDF inválido (não inicia com %PDF)")
                elif fmt == 'csv':
                    if len(response.content) < 10:
                        print(f"    ❌ Erro: CSV muito curto ou vazio")
            else:
                print(f"  ❌ {fmt.upper()}: FALHOU (Status: {response.status_code})")
                print(f"     Resposta: {response.content[:100]}")

    print("\n" + "=" * 50)
    print("✨ TESTES CONCLUÍDOS")
    print("=" * 50)

if __name__ == "__main__":
    test_reports()
