from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from apis.permissions.custom_permissions import IsDirecao, IsSecretario, IsFuncionario, IsAluno, IsEncarregado
from apis.services.document_service import DocumentService

from apis.models import Documento, SolicitacaoDocumento
from apis.serializers import (
    SolicitacaoDocumentoSerializer, SolicitacaoDocumentoListSerializer,
    SolicitacaoDocumentoAprovarSerializer, SolicitacaoDocumentoRejeitarSerializer,
    FaturaSerializer, DocumentoVerificacaoSerializer, DocumentoListSerializer,
    DocumentoSerializer
)


class DocumentoViewSet(viewsets.ModelViewSet):
    """ViewSet para Documento"""
    queryset = Documento.objects.select_related(
        'id_aluno', 'criado_por'
    ).all()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_permissions(self):
        if self.action == 'verificar':
            return []  # Acesso público
        return super().get_permissions()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id_aluno']
    search_fields = ['tipo_documento', 'uuid_documento']
    ordering_fields = ['data_emissao']
    ordering = ['-data_emissao']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentoListSerializer
        return DocumentoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tipo_documento = self.request.query_params.get('tipo_documento')
        
        if tipo_documento:
            # Se o tipo_documento for uma categoria base, fazemos a busca por aproximação
            # Isso resolve o problema de tabelas vazias no Admin quando se clica em "Declarações"
            queryset = queryset.filter(tipo_documento__icontains=tipo_documento)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def para_encarregado(self, request):
        """Retorna documentos de todos os educandos de um encarregado"""
        id_encarregado = request.query_params.get('id_encarregado')
        if not id_encarregado:
            return Response({'error': 'ID do encarregado é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        from apis.models import AlunoEncarregado
        aluno_ids = AlunoEncarregado.objects.filter(id_encarregado_id=id_encarregado).values_list('id_aluno_id', flat=True)
        documentos = self.queryset.filter(id_aluno_id__in=aluno_ids)
        
        page = self.paginate_queryset(documentos)
        if page is not None:
            serializer = DocumentoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = DocumentoListSerializer(documentos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='verificar/(?P<uuid_doc>[^/.]+)')
    def verificar(self, request, uuid_doc=None):
        """Action pública para verificar autenticidade de um documento pelo UUID"""
        try:
            documento = Documento.objects.select_related(
                'id_aluno', 'id_aluno__id_turma', 'id_aluno__id_turma__id_classe'
            ).get(uuid_documento=uuid_doc)
            serializer = DocumentoVerificacaoSerializer(documento, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Documento.DoesNotExist:
            return Response({'error': 'Documento não encontrado ou inválido'}, status=status.HTTP_404_NOT_FOUND)


class SolicitacaoDocumentoViewSet(viewsets.ModelViewSet):
    """ViewSet para SolicitacaoDocumento"""
    queryset = SolicitacaoDocumento.objects.select_related(
        'id_aluno', 'id_encarregado', 'id_funcionario'
    ).all()
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status_solicitacao', 'tipo_documento', 'id_aluno']
    search_fields = ['tipo_documento']
    ordering_fields = ['data_solicitacao']
    ordering = ['-data_solicitacao']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SolicitacaoDocumentoListSerializer
        elif self.action == 'aprovar':
            return SolicitacaoDocumentoAprovarSerializer
        elif self.action == 'rejeitar':
            return SolicitacaoDocumentoRejeitarSerializer
        return SolicitacaoDocumentoSerializer
    
    def get_queryset(self):
        """
        Filtra solicitações baseado no tipo de usuário:
        - Funcionário/Admin: vê todas as solicitações
        - Encarregado: vê apenas solicitações dos seus filhos
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Verificar se é encarregado pelo nome do modelo
        user_model_name = user.__class__.__name__
        
        if user_model_name == 'Encarregado':
            # Buscar IDs dos alunos vinculados a este encarregado
            from apis.models import AlunoEncarregado
            alunos_ids = AlunoEncarregado.objects.filter(
                id_encarregado=user.id_encarregado
            ).values_list('id_aluno', flat=True)
            
            queryset = queryset.filter(id_aluno__in=alunos_ids)
        
        return queryset


    def create(self, request, *args, **kwargs):
        """Sobrescreve criação para usar DocumentService"""
        aluno_id = request.data.get('id_aluno')
        tipo_documento = request.data.get('tipo_documento')
        canal_pagamento = request.data.get('canal_pagamento_rup', 'fisico_rup')
        encarregado_id = request.data.get('id_encarregado')
        classe_id = request.data.get('classe_solicitada')

        if not aluno_id or not tipo_documento:
            return Response({'error': 'Dados incompletos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            solicitacao, fatura = DocumentService.criar_solicitacao(
                aluno_id, tipo_documento, canal_pagamento, encarregado_id, classe_id
            )
            return Response({
                'message': 'Solicitação criada com sucesso',
                'solicitacao': SolicitacaoDocumentoSerializer(solicitacao).data,
                'fatura': FaturaSerializer(fatura).data
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Erro inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def minhas(self, request):
        """Retorna solicitações do usuário autenticado (Encarregado ou Aluno)"""
        id_encarregado = request.query_params.get('id_encarregado')
        id_aluno = request.query_params.get('id_aluno')
        
        if id_encarregado:
            solicitacoes = self.queryset.filter(id_encarregado_id=id_encarregado)
        elif id_aluno:
            solicitacoes = self.queryset.filter(id_aluno_id=id_aluno)
        else:
             # Se for admin/funcionario, talvez retornar vazio ou erro?
             # Vamos retornar erro para evitar listagem total acidental
             return Response({'error': 'ID do aluno ou encarregado é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
        page = self.paginate_queryset(solicitacoes)
        if page is not None:
            serializer = SolicitacaoDocumentoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SolicitacaoDocumentoListSerializer(solicitacoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pendentes(self, request):
        """Retorna solicitações pendentes"""
        solicitacoes = self.queryset.filter(status_solicitacao='pendente')
        serializer = SolicitacaoDocumentoListSerializer(solicitacoes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsDirecao])
    def aprovar(self, request, pk=None):
        """Aprovar solicitação de documento usando DocumentService"""
        serializer = SolicitacaoDocumentoAprovarSerializer(data=request.data)
        
        if serializer.is_valid():
            funcionario_id = serializer.validated_data['id_funcionario']
            try:
                solicitacao = DocumentService.aprovar_solicitacao(pk, funcionario_id)
                return Response({
                    'message': 'Solicitação aprovada com sucesso via DocumentService',
                    'solicitacao': SolicitacaoDocumentoSerializer(solicitacao).data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsDirecao])
    def rejeitar(self, request, pk=None):
        """Rejeitar solicitação de documento usando DocumentService"""
        serializer = SolicitacaoDocumentoRejeitarSerializer(data=request.data)
        
        if serializer.is_valid():
            funcionario_id = serializer.validated_data['id_funcionario']
            motivo = serializer.validated_data['motivo']
            try:
                solicitacao = DocumentService.rejeitar_solicitacao(pk, funcionario_id, motivo)
                return Response({
                    'message': 'Solicitação rejeitada',
                    'motivo': motivo
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'], permission_classes=[IsFuncionario])
    def confirmar_pagamento(self, request, pk=None):
        """Confirmar pagamento manual e gerar documento final"""
        funcionario_id = request.data.get('id_funcionario')
        if not funcionario_id:
            # Tentar pegar do perfil injetado pelo SchoolJWTAuthentication
            if hasattr(request, 'user_type') and request.user_type == 'funcionario':
                funcionario_id = getattr(request, 'profile_id', None)
            # Fallback para o objeto user se ele for do tipo Funcionario
            elif hasattr(request.user, 'id_funcionario'):
                funcionario_id = request.user.id_funcionario
             
        try:
            caminho_pdf = DocumentService.confirmar_pagamento_funcionario(pk, funcionario_id)
            # Construir URL completa
            from django.conf import settings
            pdf_url = request.build_absolute_uri(settings.MEDIA_URL + str(caminho_pdf))
            
            return Response({
                'message': 'Pagamento confirmado e documento gerado.',
                'download_url': pdf_url
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print("==== ERRO confirmar_pagamento ====")
            print(traceback.format_exc())
            print("=================================")
            return Response({'error': str(e), 'detalhe': traceback.format_exc()}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def imprimir_rup(self, request, pk=None):
        """Gerar e retornar URL do PDF do RUP"""
        try:
            caminho_pdf = DocumentService.gerar_comprovativo_rup(pk)
            if caminho_pdf:
                from django.conf import settings
                pdf_url = request.build_absolute_uri(settings.MEDIA_URL + str(caminho_pdf))
                return Response({'download_url': pdf_url}, status=status.HTTP_200_OK)
            return Response({'error': 'Erro ao gerar RUP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
