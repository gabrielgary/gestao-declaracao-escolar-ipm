from rest_framework import serializers
from apis.models import ConfiguracaoSistema

class ConfiguracaoSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoSistema
        fields = '__all__'
