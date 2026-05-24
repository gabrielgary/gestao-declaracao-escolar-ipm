from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apis.models.auditoria import Notificacao
from apis.serializers.notificacao_serializers import NotificacaoSerializer

class NotificacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerir as notificações do utilizador"""
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtra as notificações para o utilizador autenticado"""
        user = self.request.user
        user_type = getattr(self.request, 'user_type', None)
        
        queryset = Notificacao.objects.all()
        
        # Filtro baseado no tipo de usuário do request injetado pela nossa autenticação
        if user_type == 'funcionario':
            return queryset.filter(id_funcionario=user.id_funcionario)
        elif user_type == 'aluno':
            return queryset.filter(id_aluno=user.id_aluno)
        elif user_type == 'encarregado':
            return queryset.filter(id_encarregado=user.id_encarregado)
            
        return queryset.none()

    @action(detail=True, methods=['post'])
    def marcar_lida(self, request, pk=None):
        """Marca uma notificação específica como lida"""
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save()
        return Response({'status': 'Notificação marcada como lida'})

    @action(detail=False, methods=['post'])
    def marcar_todas_lidas(self, request):
        """Marca todas as notificações do utilizador como lidas"""
        self.get_queryset().update(lida=True)
        return Response({'status': 'Todas as notificações marcadas como lidas'})
