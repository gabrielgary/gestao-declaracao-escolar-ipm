import os
import sys
from pathlib import Path

print("=== VERIFICAÇÃO SIMPLES ===")
print(f"Diretório atual: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

backend_path = Path(".")
print(f"Backend path: {backend_path}")
print(f"Path existe: {backend_path.exists()}")

# Verificar arquivos principais
files_to_check = [
    "apis/services/academic_service.py",
    "apis/services/document_service.py", 
    "apis/models/avaliacoes.py",
    "templates/pdf/boletim.html"
]

print("\nVerificação de arquivos:")
for file_path in files_to_check:
    full_path = backend_path / file_path
    exists = full_path.exists()
    print(f"  {file_path}: {'✅' if exists else '❌'}")
    
# Verificar conteúdo do academic_service.py
academic_service_path = backend_path / "apis/services/academic_service.py"
if academic_service_path.exists():
    with open(academic_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\nAnálise do academic_service.py:")
    print(f"  Tamanho: {len(content)} caracteres")
    print(f"  Tem 'get_boletim_aluno': {'✅' if 'get_boletim_aluno' in content else '❌'}")
    print(f"  Tem 'select_related': {'✅' if 'select_related' in content else '❌'}")
    print(f"  Tem 'try:': {'✅' if 'try:' in content else '❌'}")
    print(f"  Tem 'except': {'✅' if 'except' in content else '❌'}")
    
print("\n=== FIM DA VERIFICAÇÃO ===")
