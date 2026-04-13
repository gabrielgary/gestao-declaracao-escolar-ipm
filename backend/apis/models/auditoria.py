from django.db import models
from .usuarios import Funcionario, Encarregado
from .alunos import Aluno
from .base import BaseModel
from apis.utils.upload_utils import upload_to_custom
class Notificacao(models.Model):
    """Sistema de notificações do sistema"""
    TIPOS = (
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
    )

    id_notificacao = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensagem = models.TextField(verbose_name='Mensagem')
    tipo = models.CharField(max_length=10, choices=TIPOS, default='info', verbose_name='Tipo')
    lida = models.BooleanField(default=False, verbose_name='Lida')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    
    # Destinatários (opcionais)
    id_funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes')
    id_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes')
    id_encarregado = models.ForeignKey(Encarregado, on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes')

    class Meta:
        db_table = 'notificacao'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo


class ConfiguracaoSistema(BaseModel):
    """Configurações gerais do sistema e dados da instituição"""
    nome_instituicao = models.CharField(max_length=200, verbose_name='Nome da Instituição')
    nif = models.CharField(max_length=50, verbose_name='NIF', null=True, blank=True)
    endereco = models.CharField(max_length=255, verbose_name='Endereço', null=True, blank=True)
    telefone = models.CharField(max_length=50, verbose_name='Telefone', null=True, blank=True)
    email_oficial = models.EmailField(verbose_name='Email Oficial', null=True, blank=True)
    director_geral = models.CharField(max_length=150, verbose_name='Director Geral', null=True, blank=True)
    logo = models.ImageField(upload_to=upload_to_custom, null=True, blank=True, verbose_name='Logo')
    assinatura_director = models.ImageField(upload_to=upload_to_custom, null=True, blank=True, verbose_name='Assinatura do Director Geral')
    assinatura_director_pedagogico = models.ImageField(upload_to=upload_to_custom, null=True, blank=True, verbose_name='Assinatura do Director Pedagógico')
    carimbo_instituicao = models.ImageField(upload_to=upload_to_custom, null=True, blank=True, verbose_name='Carimbo da Instituição')
    
    # Configurações de Backup
    backup_automatico = models.BooleanField(default=True, verbose_name='Backup Automático')
    frequencia_backup = models.CharField(max_length=50, default='diario', verbose_name='Frequência de Backup')
    
    class Meta:
        db_table = 'configuracao_sistema'
        verbose_name = 'Configuração do Sistema'
        verbose_name_plural = 'Configurações do Sistema'

    def __str__(self):
        return self.nome_instituicao


class Historico(models.Model):
    """Histórico de ações do sistema"""
    id_historico = models.AutoField(primary_key=True)
    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Funcionário',editable=False
    )
    id_aluno = models.ForeignKey(
        Aluno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Aluno',editable=False
    )
    tipo_accao = models.TextField(verbose_name='Ação Realizada', editable=False)
    dados_anteriores = models.JSONField(null=True, blank=True, verbose_name='Dados Anteriores',editable=False)
    dados_novos = models.JSONField(null=True, blank=True, verbose_name='Dados Novos',editable=False)
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora',editable=False)
    
    class Meta:
        db_table = 'historico'
        verbose_name = 'Histórico'
        verbose_name_plural = 'Históricos'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['data_hora']),
        ]
    
    def __str__(self):
        return f"{self.tipo_accao} - {self.data_hora}"


class HistoricoLogin(models.Model):
    """Histórico de logins"""
    id_historico_login = models.AutoField(primary_key=True)
    id_funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Funcionário',editable=False
    )
    id_aluno = models.ForeignKey(
        Aluno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Aluno',editable=False
    )
    id_encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Encarregado',editable=False
    )
    ip_usuario = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP',editable=False)
    dispositivo = models.CharField(max_length=150, null=True, blank=True, verbose_name='Dispositivo',editable=False)
    navegador = models.CharField(max_length=150, null=True, blank=True, verbose_name='Navegador',editable=False)
    hora_entrada = models.DateTimeField(auto_now_add=True, verbose_name='Hora de Entrada',editable=False)
    hora_saida = models.DateTimeField(null=True, blank=True, verbose_name='Hora de Saída',editable=False)
    
    class Meta:
        db_table = 'historico_login'
        verbose_name = 'Histórico de Login'
        verbose_name_plural = 'Históricos de Login'
        ordering = ['-hora_entrada']
    
    def __str__(self):
        return f"Login {self.id_historico_login} - {self.hora_entrada}"
