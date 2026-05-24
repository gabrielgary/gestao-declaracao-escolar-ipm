from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken

class SchoolTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Obter o payload do refresh token para extrair o user_type
        # O SimpleJWT já validou o refresh token neste ponto
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken(attrs['refresh'])
        
        # Preservar o user_type e user_id no novo access token
        # Nota: O SimpleJWT por padrão não copia claims extras do refresh para o access
        user_type = refresh.get('user_type')
        user_id = refresh.get('user_id')
        
        if user_type:
            # Adicionar ao novo access token entregue no 'access'
            from rest_framework_simplejwt.tokens import AccessToken
            access = AccessToken(data['access'])
            access['user_type'] = user_type
            access['user_id'] = user_id
            data['access'] = str(access)
            
        return data
