from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apis.models import Historico, HistoricoLogin
from apis.serializers.auditoria_serializers import HistoricoSerializer, HistoricoLoginSerializer


class HistoricoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class HistoricoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Historico (Auditoria)"""
    queryset = Historico.objects.select_related('id_funcionario', 'id_aluno').all()
    serializer_class = HistoricoSerializer
    pagination_class = HistoricoPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['tipo_accao', 'id_funcionario__nome_completo', 'id_aluno__nome_completo']
    ordering_fields = ['data_hora']
    ordering = ['-data_hora']


class HistoricoLoginViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para HistoricoLogin"""
    queryset = HistoricoLogin.objects.select_related(
        'id_funcionario', 'id_aluno', 'id_encarregado'
    ).all()
    serializer_class = HistoricoLoginSerializer
    pagination_class = HistoricoPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        'id_funcionario__nome_completo', 
        'id_aluno__nome_completo', 
        'id_encarregado__nome_completo',
        'ip_usuario'
    ]
    ordering_fields = ['hora_entrada', 'hora_saida']
    ordering = ['-hora_entrada']
