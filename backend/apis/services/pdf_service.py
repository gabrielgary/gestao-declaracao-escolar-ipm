import os
import uuid
from io import BytesIO
from django.conf import settings
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
from pypdf import PdfReader, PdfWriter

class PDFService:
    """
    Serviço para geração de documentos PDF a partir de templates HTML
    com Blindagem Digital (XMP via pypdf) mantendo suporte nativo no Windows.
    """
    
    @staticmethod
    def render_to_pdf(template_src, context_dict={}, doc_uuid=None, control_code=None):
        """
        Renderiza um template HTML para um arquivo binário PDF em memória usando xhtml2pdf.
        Injeta a camada de segurança se UUID e Código forem fornecidos.
        """
        from apis.models import ConfiguracaoSistema, Funcionario
        config = ConfiguracaoSistema.objects.first()
        
        # Buscar Diretores Ativos automaticamente
        director_geral = Funcionario.objects.filter(
            id_cargo__nome_cargo__icontains='Director Geral', 
            status_funcionario='Activo'
        ).first()
        
        subdirector_pedagogico = Funcionario.objects.filter(
            id_cargo__nome_cargo__icontains='Pedagogico', 
            status_funcionario='Activo'
        ).first()

        # Garantir que os dados estão disponíveis no template
        if 'config' not in context_dict:
            context_dict['config'] = config
        
        context_dict['director_geral_nome'] = director_geral.nome_completo if director_geral else "DOMINGOS PAULO ROMEU"
        context_dict['subdirector_ped_nome'] = subdirector_pedagogico.nome_completo if subdirector_pedagogico else "GABRIEL RUFINO CHIVIMBI"
            
        template = get_template(template_src)
        html = template.render(context_dict)
        result = BytesIO()
        
        # Função para resolver caminhos de recursos (imagens, css) no PDF
        def link_callback(uri, rel):
            sUrl = settings.STATIC_URL
            sRoot = str(settings.STATIC_ROOT) if settings.STATIC_ROOT else ''
            mUrl = settings.MEDIA_URL
            mRoot = str(settings.MEDIA_ROOT) if settings.MEDIA_ROOT else ''

            if uri.startswith(mUrl):
                path = os.path.join(mRoot, uri.replace(mUrl, ""))
            elif uri.startswith(sUrl):
                path = os.path.join(sRoot, uri.replace(sUrl, ""))
                if not os.path.isfile(path):
                    for static_dir in settings.STATICFILES_DIRS:
                         possible_path = os.path.join(str(static_dir), uri.replace(sUrl, ""))
                         if os.path.isfile(possible_path):
                             path = possible_path
                             break
            else:
                return uri

            if not os.path.isfile(path) and not uri.startswith('http'):
                 path = os.path.join(str(settings.BASE_DIR), uri.lstrip('/'))

            if not os.path.isfile(path):
                return uri
            return str(path)

        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
        
        if pdf.err:
            error_msg = f"Erro na geração do PDF: {pdf.err} errors."
            print(error_msg)
            raise Exception(error_msg)
            
        pdf_bytes = result.getvalue()
        
        if doc_uuid and control_code:
            pdf_bytes = PDFService.inject_security_layer(pdf_bytes, doc_uuid, control_code, config)
            
        return pdf_bytes

    @staticmethod
    def inject_security_layer(pdf_bytes, doc_uuid, control_code, config=None):
        """
        Injeta metadados, proteção contra cópia/edição e blindagem digital.
        """
        reader = PdfReader(BytesIO(pdf_bytes))
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # 1. Metadados
        metadata = reader.metadata
        new_metadata = {}
        if metadata:
            new_metadata.update(metadata)

        instituicao = config.nome_instituicao if config else "IPM"
        new_metadata.update({
            '/Title': f'Documento Oficial {instituicao} - {doc_uuid}',
            '/Producer': f'Sistema de Gestão Escolar {instituicao} - Proteção Avançada',
            '/CustomSecurityCode': control_code,
            '/DocumentUUID': doc_uuid
        })
        writer.add_metadata(new_metadata)

        # 2. Proteção contra Cópia e Edição conforme solicitado pelo usuário
        # Owner password é necessária para definir permissões.
        owner_pwd = f"IPM-SECURITY-{uuid.uuid4().hex[:8]}"
        
        # Permissões PDF (Bitwise):
        # Bit 3 (4) = Permite Impressão (Baixa resolução)
        # Bit 12 (2048) = Permite Impressão (Alta resolução)
        # 4 | 2048 = 2052. Todos os outros bits (Cópia, Edição, Comentário) = 0.
        
        writer.encrypt(
            user_password="", 
            owner_password=owner_pwd,
            permissions_flag=2052 # Apenas leitura e impressão permitidas
        )

        output = BytesIO()
        writer.write(output)
        return output.getvalue()

    @staticmethod
    def save_pdf(pdf_content, filename, sub_dir='documentos'):
        """
        Salva o conteúdo binário do PDF no diretório de mídia
        """
        dir_path = os.path.join(settings.MEDIA_ROOT, sub_dir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'wb') as f:
            f.write(pdf_content)
            
        # Retorna o caminho relativo para salvar no banco de dados
        rel_path = os.path.join(sub_dir, filename).replace('\\', '/')
        return rel_path
