from django.db import models
import uuid
from .usuarios import Funcionario
from .alunos import Aluno
from .usuarios import Encarregado
from .academico import Classe
from .academico import Classe  # Importado para referência na solicitação


class HistoricoTurmaAluno(models.Model):
    """Histórico de turmas do aluno para rastreabilidade"""
    
    id_historico = models.AutoField(primary_key=True)
    id_aluno = models.ForeignKey(
        Aluno,
        on_delete=models.CASCADE,
        related_name='historico_turmas',
        verbose_name='Aluno'
    )
    id_turma = models.ForeignKey(
        'apis.Turma',
        on_delete=models.CASCADE,
        verbose_name='Turma'
    )
    id_classe = models.ForeignKey(
        Classe,
        on_delete=models.CASCADE,
        verbose_name='Classe'
    )
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Fim'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    ano_letivo = models.CharField(
        max_length=9,
        default='2024',
        verbose_name='Ano Letivo'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        db_table = 'historico_turma_aluno'
        verbose_name = 'Histórico de Turma do Aluno'
        verbose_name_plural = 'Históricos de Turmas dos Alunos'
        ordering = ['-data_inicio']
        indexes = [
            models.Index(fields=['id_aluno']),
            models.Index(fields=['id_aluno', 'ativo']),
            models.Index(fields=['id_classe']),
        ]
    
    def __str__(self):
        return f"{self.id_aluno.nome_completo} - {self.id_classe.nivel}ª ({'Atual' if self.ativo else 'Histórica'})"


def salvar_historico_turma_aluno(aluno, nova_turma):
    """
    Função para salvar histórico de turma do aluno
    Sempre que o aluno for associado a uma turma
    """
    from django.utils import timezone
    
    # Desativa turma anterior
    HistoricoTurmaAluno.objects.filter(
        id_aluno=aluno,
        ativo=True
    ).update(
        data_fim=timezone.now().date(),
        ativo=False
    )
    
    # Cria novo histórico
    return HistoricoTurmaAluno.objects.create(
        id_aluno=aluno,
        id_turma=nova_turma,
        id_classe=nova_turma.id_classe,  # ← VEM DA TURMA!
        data_inicio=timezone.now().date(),
        ano_letivo=str(timezone.now().year),
        ativo=True
    )


class Documento(models.Model):
    TIPO_DOCUMENTO_CHOICES=[
        ('DECLARAÇÃO','DECLARAÇÃO'),
        ('BOLETIM','BOLETIM'),
        ('CERTIFICADO','CERTIFICADO'),
    ]
    """Documentos gerados (PDFs)"""
    id_documento = models.AutoField(primary_key=True)
    id_aluno = models.ForeignKey(
        Aluno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Aluno'
    )
    tipo_documento = models.CharField(max_length=100,choices=TIPO_DOCUMENTO_CHOICES, verbose_name='Tipo de Documento')
    caminho_pdf = models.FileField(upload_to="documentos/documents/pdfs/", null=True)
    #models.TextField(null=True, blank=True, verbose_name='Caminho do PDF')
    #imagem_carimbo = models.TextField(null=True, blank=True, verbose_name='Carimbo/Assinatura')
    uuid_documento = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='CÓDIGO ÚNICO DO DOCUMENTO')
    codigo_seguranca = models.CharField(max_length=10, null=True, blank=True, verbose_name='CÓDIGO DE SEGURANÇA')
    criado_por = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_criados',
        verbose_name='Criado por'
    )
    data_emissao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Emissão')
    
    class Meta:
        db_table = 'documento'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-data_emissao']
        indexes = [
            models.Index(fields=['id_aluno']),
            models.Index(fields=['uuid_documento']),
        ]
    
    def __str__(self):
        return f"{self.tipo_documento} - {self.uuid_documento}"


class SolicitacaoDocumento(models.Model):
    """Solicitações de documentos"""
    
    STATUS_CHOICES = [
        ('pendente', 'Aguardando Pagamento'),
        ('pago', 'Pago (Aguardando/Processando)'),
        ('disponivel', 'Concluído e Disponível'),
        ('rejeitado', 'Rejeitado / Cancelado'),
    ]

    CANAL_PAGAMENTO_CHOICES = [
        ('express', 'Multicaixa Express'),
        ('fisico_rup', 'Impressão de RUP (Físico)'),
    ]
    
    id_solicitacao = models.AutoField(primary_key=True)
    id_aluno = models.ForeignKey(
        Aluno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Aluno'
    )
    id_encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Encarregado'
    )
    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_gerenciadas',
        verbose_name='Funcionário Responsável'
    )
    
    tipo_documento = models.CharField(max_length=100, verbose_name='Tipo de Documento')
    status_solicitacao = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    # Novos campos para fluxo RUP e Classe
    rupe = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='RUPE/Referência')
    valor_rupe = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Valor do RUP')
    classe_solicitada = models.ForeignKey(
        Classe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Classe Solicitada'
    )

    canal_pagamento_rup = models.CharField(
        max_length=20,
        choices=CANAL_PAGAMENTO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Canal de Pagamento'
    )
    data_expiracao_rup = models.DateTimeField(null=True, blank=True, verbose_name='Expiração do RUP')
    caminho_arquivo = models.FileField(
        upload_to='documentos/',
        null=True,
        blank=True,
        verbose_name='Arquivo Gerado (PDF)'
    )
    uuid_documento = models.UUIDField(null=True, blank=True, verbose_name='UUID do Documento')
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Solicitação')
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name='Data de Aprovação')
    
    class Meta:
        db_table = 'solicitacao_documento'
        verbose_name = 'Solicitação de Documento'
        verbose_name_plural = 'Solicitações de Documentos'
        ordering = ['-data_solicitacao']
        indexes = [
            models.Index(fields=['status_solicitacao']),
            models.Index(fields=['id_aluno']),
            models.Index(fields=['data_solicitacao']),
        ]
    
    def __str__(self):
        return f"{self.tipo_documento} - {self.status_solicitacao}"
