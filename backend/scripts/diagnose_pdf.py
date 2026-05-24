import os
import django
import sys
import traceback
from io import BytesIO

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.template import Context, Template
from xhtml2pdf import pisa
from apis.services.document_service import DocumentService
from apis.models import SolicitacaoDocumento

LOG_FILE = 'diagnosis.log'

def log(msg):
    print(msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")

def clear_log():
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("--- START DIAGNOSIS ---\n")

def test_simple_pdf():
    log("\n[TEST 1] Generating Simple PDF (Hello WorldString)...")
    try:
        html = "<html><body><h1>Hello World</h1></body></html>"
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if pdf.err:
            log(f"FAIL: pisaDocument returned err={pdf.err}")
        else:
            log("SUCCESS: Simple PDF generated.")
    except Exception as e:
        log(f"CRITICAL FAIL: {str(e)}")
        traceback.print_exc(file=open(LOG_FILE, 'a'))

def test_template_render():
    log("\n[TEST 2] Loading and Rendering Template (no pisa)...")
    try:
        from django.template.loader import get_template
        # Using the template likely used by Solicitacao 9
        # Assuming Solicitacao 9 is a Declaration or similar.
        # Let's verify Solicitacao 9 first.
        sol = SolicitacaoDocumento.objects.filter(id_solicitacao=9).first()
        if not sol:
            log("SKIP: Solicitacao 9 not found for template check.")
            return

        template_name = 'pdf/declaracao_matricula.html' 
        # Logic matches DocumentService
        if 'CERTIFICADO' in sol.tipo_documento.upper():
             template_name = 'pdf/certificado.html'
        elif 'BOLETIM' in sol.tipo_documento.upper():
             template_name = 'pdf/boletim.html'
        elif 'APROVEITAMENTO' in sol.tipo_documento.upper():
             template_name = 'pdf/declaracao_aproveitamento.html'
        
        log(f"Target Template: {template_name}")
        
        # Test loading
        valid_tpl = get_template(template_name)
        log("Template loaded successfully.")
        
        # Test rendering with Minimal Context
        ctx = {
            'aluno': sol.id_aluno,
            'solicitacao': sol,
            'hoje': '2025-01-31',
            'site_url': 'http://localhost'
        }
        rendered_html = valid_tpl.render(ctx)
        log(f"Template rendered successfully (Length: {len(rendered_html)})")
        return rendered_html
    except Exception as e:
        log(f"FAIL Template Render: {str(e)}")
        traceback.print_exc(file=open(LOG_FILE, 'a'))
        return None

def test_full_flow_with_link_callback(rendered_html):
    log("\n[TEST 3] Generating PDF from Rendered Template (with link_callback)...")
    if not rendered_html:
        log("SKIP: No HTML to test.")
        return

    try:
        from apis.services.pdf_service import PDFService
        # Check link_callback directly
        log("Testing manually calling PDFService generation...")
        
        result = BytesIO()
        
        # Use the exact link callback from PDFService logic (simulated or imported)
        # We will import PDFService and inspect/use its logic if possible, 
        # but pisaDocument calls it internally.
        
        # Override PDFService temporarily to print inside callback? 
        # No, let's just use it.
        
        # Using pisa directly with the 'broken' callback logic if we want to isolate,
        # but better to call PDFService method if public?
        # render_to_pdf is static.
        
        # Let's construct a context mock to match TEST 2
        # Use PDFService.render_to_pdf
        # But we need to pass template path, not html content.
        
        pdf_content = PDFService.render_to_pdf('pdf/declaracao_matricula.html', {})
        # Note: Empty context failure is expected if template needs vars.
        # But if it crashes with NotImplementedType, that's significant.
        
        log("PDFService.render_to_pdf(empty_context) returned result.")
    except Exception as e:
        log(f"FAIL PDFService: {str(e)}")
        traceback.print_exc(file=open(LOG_FILE, 'a'))

def test_real_solicitacao_9():
    log("\n[TEST 4] Full DocumentService.confirmar_pagamento_funcionario for ID 9...")
    try:
        from apis.models import Funcionario
        func = Funcionario.objects.first()
        if not func:
            log("No funcionario found.")
            return

        path = DocumentService.confirmar_pagamento_funcionario(9, func.id_funcionario)
        log(f"SUCCESS: Generated at {path}")
    except Exception as e:
        log(f"FAIL Real Flow: {str(e)}")
        traceback.print_exc(file=open(LOG_FILE, 'a'))

if __name__ == '__main__':
    clear_log()
    test_simple_pdf()
    html = test_template_render()
    # test_full_flow_with_link_callback(html) # Skipping partial, jumping to full flow
    test_real_solicitacao_9()
