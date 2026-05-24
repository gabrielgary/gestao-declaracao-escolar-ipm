from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from apis.models import Funcionario, Aluno, Encarregado

class SchoolJWTAuthentication(JWTAuthentication):
    """
    Autenticação JWT customizada que injeta os dados do perfil no request
    """
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        
        # Injetar o payload no request para as permissões
        request.auth_payload = validated_token
        
        # No Django REST, request.user é obrigatório para muitas funcionalidades
        # Vamos tentar associar a um usuário real do Django se existir, 
        # ou retornar o objeto do perfil
        user_id = validated_token.get('user_id')
        user_type = validated_token.get('user_type')
        
        user = self.get_user(validated_token)
        
        # Adicionar informações extras ao request
        request.user_type = user_type
        request.profile_id = user_id
        
        return user, validated_token

    def get_user(self, validated_token):
        """
        Retorna o objeto do perfil (Funcionario, Aluno ou Encarregado)
        baseado no user_type do token.
        """
        user_id = validated_token.get('user_id')
        user_type = validated_token.get('user_type')
        
        try:
            if user_type == 'funcionario':
                return Funcionario.objects.get(id_funcionario=user_id)
            elif user_type == 'aluno':
                return Aluno.objects.get(id_aluno=user_id)
            elif user_type == 'encarregado':
                return Encarregado.objects.get(id_encarregado=user_id)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Perfil {user_type} não encontrado para o ID {user_id}")
        
        return None
