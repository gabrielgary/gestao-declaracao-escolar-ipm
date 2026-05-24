import os
import sys
import django
from io import BytesIO
from pypdf import PdfReader

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.services.pdf_service import PDFService
from apis.services.document_service import DocumentService
from apis.models import Aluno, SolicitacaoDocumento

def test_security_payload():
    print("🛡️ Iniciando Teste de Integridade Digital...")
    
    # 1. Simular Documento
    doc_uuid = "test-uuid-001-security"
    control_code = "SEC-TEST"
    
    context = {
        'aluno': {'nome_completo': 'Aluno de Teste Segurança'},
        'hoje': django.utils.timezone.now(),
        'site_url': 'http://localhost:5173',
        'doc_uuid': doc_uuid,
        'codigo_seguranca': control_code
    }
    
    # 2. Gerar PDF com a nova camada
    print("⚙️ Gerando PDF com WeasyPrint + Camada pypdf...")
    pdf_content = PDFService.render_to_pdf(
        'pdf/base_documento.html', 
        context, 
        doc_uuid=doc_uuid, 
        control_code=control_code
    )
    
    # 3. Validar Metadados
    print("🔍 Analisando metadados internos (XMP)...")
    reader = PdfReader(BytesIO(pdf_content))
    meta = reader.metadata
    
    print(f"   - Title: {meta.get('/Title')}")
    print(f"   - Producer: {meta.get('/Producer')}")
    print(f"   - Custom Security Code: {meta.get('/CustomSecurityCode')}")
    
    assert doc_uuid in meta.get('/Title'), "❌ UUID não encontrado nos metadados!"
    assert control_code == meta.get('/CustomSecurityCode'), "❌ Código de Segurança não bate!"
    
    print("\n✅ TESTE BEM SUCEDIDO: A blindagem digital está ativa!")

if __name__ == "__main__":
    try:
        test_security_payload()
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        sys.exit(1)
