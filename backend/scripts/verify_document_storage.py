import os
import django
import sys

# Setup Django environment
sys.path.append('c:/wamp64/www/gestao-escolar-fim-course/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apis.models import Aluno, SolicitacaoDocumento
from apis.services.document_service import DocumentService
from django.utils import timezone

def verify():
    print("Testing document path organization...")
    aluno = Aluno.objects.first()
    if not aluno:
        print("Error: No students found in database.")
        return

    print(f"Using student: {aluno.nome_completo} (BI: {aluno.numero_bi})")
    
    # Test _get_document_path
    path = DocumentService._get_document_path(aluno, "DECLARACAO")
    print(f"Generated path prefix: {path}")
    
    expected_bi = aluno.numero_bi or aluno.numero_matricula or str(aluno.id_aluno)
    expected_bi = expected_bi.replace('/', '_').replace(' ', '_')
    now = timezone.now()
    expected_path = f"{expected_bi}/documentos/DECLARACAO/{now.year}/{now.month:02d}"
    
    if path == expected_path:
        print("SUCCESS: Path generated correctly.")
    else:
        print(f"FAILURE: Expected {expected_path}, got {path}")

    # Test path normalization (slashes)
    from apis.services.pdf_service import PDFService
    rel_path = PDFService.save_pdf(b"test content", "test.pdf", sub_dir=path)
    print(f"Saved PDF relative path: {rel_path}")
    
    if '\\' in rel_path:
        print("FAILURE: Relative path contains backslashes.")
    else:
        print("SUCCESS: Relative path uses forward slashes.")

    # Cleanup test file
    full_path = os.path.join('c:/wamp64/www/gestao-escolar-fim-course/backend/media', rel_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        print("Test file removed.")

if __name__ == "__main__":
    verify()
