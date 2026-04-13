from rest_framework import serializers
from apis.models import Inscricao, Matricula, Historico, HistoricoLogin


class InscricaoSerializer(serializers.ModelSerializer):
    """Serializer para Inscricao"""
    
    class Meta:
        model = Inscricao
        fields = [
            'id_inscricao', 'data_inscricao', 'nome_candidato',
            'documento_candidato', 'resultado_avaliacao'
        ]
        read_only_fields = ['id_inscricao', 'data_inscricao']


class MatriculaSerializer(serializers.ModelSerializer):
    """Serializer para Matricula"""
    aluno_nome = serializers.CharField(source='id_aluno.nome_completo', read_only=True)
    turma_codigo = serializers.CharField(source='id_turma.codigo_turma', read_only=True)
    
    class Meta:
        model = Matricula
        fields = [
            'id_matricula', 'id_aluno', 'aluno_nome', 'id_turma',
            'turma_codigo', 'data_matricula', 'ativo'
        ]
        read_only_fields = ['id_matricula', 'data_matricula']


class HistoricoSerializer(serializers.ModelSerializer):
    """Serializer para Historico"""
    usuario_nome = serializers.SerializerMethodField()
    usuario_tipo = serializers.SerializerMethodField()
    usuario_img = serializers.SerializerMethodField()
    
    class Meta:
        model = Historico
        fields = [
            'id_historico', 'usuario_nome', 'usuario_tipo', 'usuario_img',
            'tipo_accao', 'dados_anteriores', 'dados_novos', 'data_hora'
        ]
        read_only_fields = ['id_historico', 'data_hora']

    def get_usuario_nome(self, obj):
        if obj.id_funcionario: return obj.id_funcionario.nome_completo
        if obj.id_aluno: return obj.id_aluno.nome_completo
        return "Administrador"

    def get_usuario_tipo(self, obj):
        if obj.id_funcionario: return "Funcionário"
        if obj.id_aluno: return "Aluno"
        return "Administrador"

    def get_usuario_img(self, obj):
        request = self.context.get('request')
        user_obj = obj.id_funcionario or obj.id_aluno
        if user_obj and hasattr(user_obj, 'img_path') and user_obj.img_path:
            if request:
                return request.build_absolute_uri(user_obj.img_path.url)
            return user_obj.img_path.url
        return None


class HistoricoLoginSerializer(serializers.ModelSerializer):
    """Serializer para HistoricoLogin"""
    usuario_nome = serializers.SerializerMethodField()
    usuario_tipo = serializers.SerializerMethodField()
    usuario_img = serializers.SerializerMethodField()
    
    class Meta:
        model = HistoricoLogin
        fields = [
            'id_historico_login', 'usuario_nome', 'usuario_tipo', 'usuario_img',
            'ip_usuario', 'dispositivo', 'navegador', 'hora_entrada', 'hora_saida'
        ]
        read_only_fields = ['id_historico_login', 'hora_entrada']

    def get_usuario_nome(self, obj):
        if obj.id_funcionario: return obj.id_funcionario.nome_completo
        if obj.id_aluno: return obj.id_aluno.nome_completo
        if obj.id_encarregado: return obj.id_encarregado.nome_completo
        return "Desconhecido"

    def get_usuario_tipo(self, obj):
        if obj.id_funcionario: return "Funcionário"
        if obj.id_aluno: return "Aluno"
        if obj.id_encarregado: return "Encarregado"
        return "N/A"

    def get_usuario_img(self, obj):
        request = self.context.get('request')
        user_obj = obj.id_funcionario or obj.id_aluno or obj.id_encarregado
        if user_obj and user_obj.img_path:
            if request:
                return request.build_absolute_uri(user_obj.img_path.url)
            return user_obj.img_path.url
        return None
