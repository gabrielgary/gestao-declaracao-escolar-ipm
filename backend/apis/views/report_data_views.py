from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apis.models import Aluno, Funcionario, SolicitacaoDocumento, Historico, HistoricoLogin, ConfiguracaoSistema
from apis.serializers.auditoria_serializers import HistoricoSerializer, HistoricoLoginSerializer
from apis.serializers.configuracao_serializers import ConfiguracaoSistemaSerializer

# Serializers customizados para incluir IDs de filtragem profunda
class AlunoReportSerializer(serializers.ModelSerializer):
    turma_codigo = serializers.CharField(source='id_turma.codigo_turma', read_only=True)
    id_classe = serializers.IntegerField(source='id_turma.id_classe.id_classe', read_only=True)
    classe_nivel = serializers.IntegerField(source='id_turma.id_classe.nivel', read_only=True)
    id_curso = serializers.IntegerField(source='id_turma.id_curso.id_curso', read_only=True)
    curso_nome = serializers.CharField(source='id_turma.id_curso.nome_curso', read_only=True)
    
    class Meta:
        model = Aluno
        fields = [
            'id_aluno', 'nome_completo', 'numero_bi', 'genero', 
            'id_turma', 'turma_codigo', 'id_classe', 'classe_nivel',
            'id_curso', 'curso_nome', 'status_aluno', 'modo_user'
        ]

class SolicitacaoReportSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='id_aluno.nome_completo', read_only=True)
    
    class Meta:
        model = SolicitacaoDocumento
        fields = [
            'id_solicitacao', 'aluno_nome', 'tipo_documento', 
            'data_solicitacao', 'status_solicitacao', 'valor_rupe'
        ]

class FuncionarioReportSerializer(serializers.ModelSerializer):
    cargo_nome = serializers.CharField(source='id_cargo.nome_cargo', read_only=True)
    
    class Meta:
        model = Funcionario
        fields = [
            'id_funcionario', 'nome_completo', 'id_cargo', 'cargo_nome', 
            'telefone', 'status_funcionario', 'genero'
        ]

class ReportDataViewSet(viewsets.ViewSet):
    """
    ViewSet para fornecer coleções completas de dados para filtragem no frontend.
    """
    permission_classes = [IsAuthenticated]

    def list_solicitacoes(self, request):
        queryset = SolicitacaoDocumento.objects.select_related('id_aluno').all()
        serializer = SolicitacaoReportSerializer(queryset, many=True)
        return Response(serializer.data)

    def list_alunos(self, request):
        queryset = Aluno.objects.select_related('id_turma', 'id_turma__id_classe', 'id_turma__id_curso').all()
        serializer = AlunoReportSerializer(queryset, many=True)
        return Response(serializer.data)

    def list_funcionarios(self, request):
        queryset = Funcionario.objects.select_related('id_cargo').all()
        serializer = FuncionarioReportSerializer(queryset, many=True)
        return Response(serializer.data)

    def list_auditoria(self, request):
        queryset = Historico.objects.select_related('id_funcionario', 'id_aluno').order_by('-data_hora')[:1000]
        serializer = HistoricoSerializer(queryset, many=True)
        return Response(serializer.data)

    def list_logins(self, request):
        queryset = HistoricoLogin.objects.select_related('id_funcionario', 'id_aluno', 'id_encarregado').order_by('-hora_entrada')[:500]
        serializer = HistoricoLoginSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_config(self, request):
        config = ConfiguracaoSistema.objects.first()
        if not config:
            return Response({"detail": "Não configurado"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ConfiguracaoSistemaSerializer(config, context={'request': request})
        return Response(serializer.data)
