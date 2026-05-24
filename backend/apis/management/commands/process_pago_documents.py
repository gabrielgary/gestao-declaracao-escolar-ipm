from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from apis.models import SolicitacaoDocumento
from apis.services.document_service import DocumentService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Processa solicitações pagas que ainda não possuem PDF gerado'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando processamento de documentos pagos...'))
        
        # 1. Buscar solicitações em estado 'pago' que não tenham arquivo gerado
        # Nota: Algumas podem ter caminho_arquivo vazio ou nulo
        solicitacoes_pendentes = SolicitacaoDocumento.objects.filter(
            status_solicitacao='pago'
        ).filter(
            models.Q(caminho_arquivo__isnull=True) | models.Q(caminho_arquivo='')
        )

        total = solicitacoes_pendentes.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhuma solicitação pendente encontrada.'))
            return

        self.stdout.write(f'Encontradas {total} solicitações para processar.')
        
        sucesso = 0
        erro = 0

        for solicitacao in solicitacoes_pendentes:
            try:
                self.stdout.write(f'Processando solicitacao ID {solicitacao.id_solicitacao} ({solicitacao.tipo_documento})...')
                
                # Chamar o serviço de geração
                resultado = DocumentService.gerar_pdf_documento(solicitacao.id_solicitacao)
                
                if resultado:
                    sucesso += 1
                    self.stdout.write(self.style.SUCCESS(f'Documento gerado com sucesso: {resultado}'))
                else:
                    erro += 1
                    self.stdout.write(self.style.ERROR(f'Falha ao gerar documento para ID {solicitacao.id_solicitacao}'))
            
            except Exception as e:
                erro += 1
                self.stdout.write(self.style.ERROR(f'Erro crítico na solicitação {solicitacao.id_solicitacao}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(
            f'Processamento concluído: {sucesso} gerados, {erro} falhas de um total de {total}.'
        ))
