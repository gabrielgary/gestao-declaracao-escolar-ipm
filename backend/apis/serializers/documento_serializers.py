from rest_framework import serializers
from apis.models import Documento, SolicitacaoDocumento


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para Documento"""
    aluno_nome = serializers.CharField(source='id_aluno.nome_completo', read_only=True)
    criado_por_nome = serializers.CharField(source='criado_por.nome_completo', read_only=True)
    
    class Meta:
        model = Documento
        fields = [
            'id_documento', 'id_aluno', 'aluno_nome', 'tipo_documento',
            'caminho_pdf', 'uuid_documento',
            'criado_por', 'criado_por_nome', 'data_emissao'
        ]
        read_only_fields = ['id_documento', 'uuid_documento', 'data_emissao']


class DocumentoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Documentos"""
    aluno_nome = serializers.CharField(source='id_aluno.nome_completo', read_only=True)
    aluno_img = serializers.SerializerMethodField()
    classe = serializers.CharField(source='id_aluno.id_turma.id_classe.nivel', read_only=True)
    curso = serializers.CharField(source='id_aluno.id_turma.id_curso.nome_curso', read_only=True)
    
    class Meta:
        model = Documento
        fields = [
            'id_documento', 'tipo_documento', 'aluno_nome', 'aluno_img', 
            'classe', 'curso', 'caminho_pdf', 'uuid_documento', 'data_emissao'
        ]

    def get_aluno_img(self, obj):
        request = self.context.get('request')
        if obj.id_aluno and obj.id_aluno.img_path:
            if request:
                return request.build_absolute_uri(obj.id_aluno.img_path.url)
            return obj.id_aluno.img_path.url
        return None


class SolicitacaoDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para SolicitacaoDocumento"""
    aluno_nome = serializers.CharField(source='id_aluno.nome_completo', read_only=True)
    encarregado_nome = serializers.CharField(source='id_encarregado.nome_completo', read_only=True)
    funcionario_nome = serializers.CharField(source='id_funcionario.nome_completo', read_only=True)
    
    class Meta:
        model = SolicitacaoDocumento
        fields = [
            'id_solicitacao', 'id_aluno', 'aluno_nome', 'id_encarregado', 'encarregado_nome',
            'id_funcionario', 'funcionario_nome', 'tipo_documento', 'status_solicitacao',
            'canal_pagamento_rup', 'rupe', 'valor_rupe', 'data_expiracao_rup',
            'caminho_arquivo', 'uuid_documento', 'data_solicitacao', 'data_aprovacao'
        ]
        read_only_fields = ['id_solicitacao', 'data_solicitacao', 'data_aprovacao', 'data_expiracao_rup', 'rupe', 'valor_rupe']


class SolicitacaoDocumentoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Solicitações"""
    aluno_nome = serializers.CharField(source='id_aluno.nome_completo', read_only=True)
    aluno_img = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitacaoDocumento
        fields = [
            'id_solicitacao', 'tipo_documento', 'rupe', 'aluno_nome', 'aluno_img',
            'status_solicitacao', 'data_solicitacao', 'caminho_arquivo', 
            'valor_rupe', 'data_expiracao_rup'
        ]

    def get_aluno_img(self, obj):
        request = self.context.get('request')
        if obj.id_aluno and obj.id_aluno.img_path:
            if request:
                return request.build_absolute_uri(obj.id_aluno.img_path.url)
            return obj.id_aluno.img_path.url
        return None


class SolicitacaoDocumentoAprovarSerializer(serializers.Serializer):
    """Serializer para aprovar solicitação"""
    id_funcionario = serializers.IntegerField()
    observacao = serializers.CharField(required=False, allow_blank=True)


class SolicitacaoDocumentoRejeitarSerializer(serializers.Serializer):
    """Serializer para rejeitar solicitação"""
    id_funcionario = serializers.IntegerField()
    motivo = serializers.CharField(required=True)


class DocumentoVerificacaoSerializer(serializers.ModelSerializer):
    """Serializer para verificação pública de autenticidade"""
    aluno_nome_ofuscado = serializers.SerializerMethodField()
    bi_aluno_ofuscado = serializers.SerializerMethodField()
    instituicao = serializers.SerializerMethodField()
    periodo_letivo = serializers.CharField(source='id_aluno.id_turma.ano', read_only=True)
    classe = serializers.CharField(source='id_aluno.id_turma.id_classe.nivel', read_only=True)
    download_url = serializers.SerializerMethodField()
    codigo_seguranca = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = [
            'uuid_documento', 'codigo_seguranca', 'tipo_documento', 
            'aluno_nome_ofuscado', 'bi_aluno_ofuscado',
            'instituicao', 'data_emissao', 'classe', 'periodo_letivo',
            'download_url'
        ]

    def get_codigo_seguranca(self, obj):
        return obj.codigo_seguranca if obj.codigo_seguranca else "N/A"

    def get_download_url(self, obj):
        request = self.context.get('request')
        if obj.caminho_pdf:
            if request:
                return request.build_absolute_uri(obj.caminho_pdf.url)
            return obj.caminho_pdf.url
        return None

    def get_aluno_nome_ofuscado(self, obj):
        if not obj.id_aluno:
            return "N/A"
        nome = obj.id_aluno.nome_completo
        partes = nome.split()
        if len(partes) > 1:
            return f"{partes[0]} {' '.join(['*' * len(p) for p in partes[1:-1]])} {partes[-1]}"
        return f"{nome[0]}{'*' * (len(nome)-1)}"

    def get_bi_aluno_ofuscado(self, obj):
        if not obj.id_aluno or not obj.id_aluno.numero_bi:
            return "N/A"
        bi = obj.id_aluno.numero_bi
        return f"{bi[:3]}******{bi[-2:]}"

    def get_instituicao(self, obj):
        return "Instituto Politécnico do Maiombe"
