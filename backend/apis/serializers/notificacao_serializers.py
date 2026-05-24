from rest_framework import serializers
from apis.models.auditoria import Notificacao

class NotificacaoSerializer(serializers.ModelSerializer):
    """Serializer para o sistema de notificações"""
    class Meta:
        model = Notificacao
        fields = '__all__'
        read_only_fields = ['data_criacao']
