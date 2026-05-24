import os
import django
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apis.services.document_service import DocumentService
from apis.models import SolicitacaoDocumento, Funcionario

SOLICITACAO_ID = 9

try:
    print(f"--- Debugging Solicitacao {SOLICITACAO_ID} ---")
    solicitacao = SolicitacaoDocumento.objects.get(id_solicitacao=SOLICITACAO_ID)
    print(f"Tipo Documento: {solicitacao.tipo_documento}")
    print(f"Status Atual: {solicitacao.status_solicitacao}")
    
    # Simulate an employee confirming (using admin/first employee)
    funcionario = Funcionario.objects.first()
    if not funcionario:
        print("CRITICAL: Nenhum funcionário encontrado no banco.")
        # Create dummy if needed or fail
    else:
        print(f"Using Funcionario: {funcionario.nome_completo}")
        
    print("Attempting confirmation...")
    path = DocumentService.confirmar_pagamento_funcionario(SOLICITACAO_ID, funcionario.id_funcionario)
    print(f"SUCCESS! PDF Path: {path}")

except Exception as e:
    with open('debug_log.txt', 'w') as f:
        f.write("\n!!! EXCEPTION CAUGHT !!!\n")
        f.write(str(e) + "\n")
        f.write("\n--- Traceback ---\n")
        traceback.print_exc(file=f)
    print("Error logged to debug_log.txt")
