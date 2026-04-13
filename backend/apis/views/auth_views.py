from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from apis.models import Funcionario, Aluno, Encarregado, HistoricoLogin


def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent_info(request):
    """Extrai informações detalhadas do User-Agent utilizando a biblioteca user_agents"""
    from user_agents import parse
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(ua_string)
    
    # Determinar tipo de dispositivo
    if user_agent.is_mobile:
        dispositivo = "Mobile"
    elif user_agent.is_tablet:
        dispositivo = "Tablet"
    elif user_agent.is_pc:
        dispositivo = "Desktop"
    else:
        dispositivo = "Desconhecido"

    # Capturar Navegador e SO
    navegador = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    so = f"{user_agent.os.family} {user_agent.os.version_string}"
    
    return {
        'dispositivo': dispositivo,
        'navegador': f"{navegador} ({so})"
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Endpoint de login para Funcionários, Alunos e Encarregados
    
    Body:
    {
        "email": "usuario@exemplo.com",
        "senha": "senha123",
        "tipo_usuario": "funcionario" | "aluno" | "encarregado"
    }
    """
    email = request.data.get('email')
    senha = request.data.get('senha')
    tipo_usuario = request.data.get('tipo_usuario', 'funcionario')
    
    if not email or not senha:
        return Response(
            {'error': 'Email e senha são obrigatórios'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = None
    user_data = {}
    
    try:
        # Buscar usuário baseado no tipo
        if tipo_usuario == 'funcionario':
            user = Funcionario.objects.get(email=email)
            if check_password(senha, user.senha_hash):
                user_data = {
                    'id': user.id_funcionario,
                    'tipo': 'funcionario',
                    'nome': user.nome_completo,
                    'email': user.email,
                    'cargo': user.id_cargo.nome_cargo if user.id_cargo else None,
                    'status': user.status_funcionario,
                    'img_path': request.build_absolute_uri(user.img_path.url) if user.img_path else None
                }
                if user.status_funcionario != 'Activo':
                    return Response(
                        {'error': 'A sua conta de funcionário está inativa.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                cargo_nome = user.id_cargo.nome_cargo if user.id_cargo else None
                if cargo_nome not in ['Secretário']:
                    return Response(
                        {'error': 'Apenas funcionários com o cargo de Secretário podem aceder a este portal. Directores devem usar o painel administrativo.'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Atualizar status online
                user.is_online = True
                user.save()
            else:
                return Response(
                    {'error': 'Dados incorretos'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        elif tipo_usuario == 'aluno':
            user = Aluno.objects.get(email=email)
            if check_password(senha, user.senha_hash):
                user_data = {
                    'id': user.id_aluno,
                    'tipo': 'aluno',
                    'nome': user.nome_completo,
                    'email': user.email,
                    'numero_matricula': user.numero_matricula,
                    'turma': user.id_turma.codigo_turma if user.id_turma else None,
                    'status': user.status_aluno,
                    'img_path': request.build_absolute_uri(user.img_path.url) if user.img_path else None
                }
                if user.modo_user == 'Inativo':
                    return Response(
                        {'error': 'A sua conta de Aluno está inativa. Por favor, contacte a secretaria.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                if user.status_aluno not in ['Activo', 'Finalizou']:
                    return Response(
                        {'error': f'O seu estado atual ({user.status_aluno}) não permite o acesso ao portal.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                # Atualizar status online
                user.is_online = True
                user.save()
            else:
                return Response(
                    {'error': 'Dados Incorretos'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        elif tipo_usuario == 'encarregado':
            user = Encarregado.objects.get(email=email)
            if check_password(senha, user.senha_hash):
                user_data = {
                    'id': user.id_encarregado,
                    'tipo': 'encarregado',
                    'nome': user.nome_completo,
                    'email': user.email,
                    'img_path': request.build_absolute_uri(user.img_path.url) if user.img_path else None
                }
                if user.modo_user == 'Inativo':
                    return Response(
                        {'error': 'A sua conta de Encarregado está inativa. Por favor, contacte o administrador.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                # Atualizar status online
                user.is_online = True
                user.save()
            else:
                return Response(
                    {'error': 'Dados Incorrecta'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                {'error': 'Tipo de usuário inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Gerar tokens JWT
        refresh = RefreshToken()
        
        # Inserir claims tanto no Refresh quanto no Access Token inicial
        refresh['user_id'] = user_data['id']
        refresh['user_type'] = user_data['tipo']
        if user_data['tipo'] == 'funcionario':
            refresh['cargo'] = user_data.get('cargo')
        
        # Importante: O SimpleJWT não copia claims customizados para o access_token automaticamente
        access = refresh.access_token
        access['user_id'] = user_data['id']
        access['user_type'] = user_data['tipo']
        if user_data['tipo'] == 'funcionario':
            access['cargo'] = user_data.get('cargo')
        
        # Registrar histórico de login
        user_agent_info = get_user_agent_info(request)
        historico_data = {
            'ip_usuario': get_client_ip(request),
            'dispositivo': user_agent_info['dispositivo'],
            'navegador': user_agent_info['navegador']
        }
        
        if tipo_usuario == 'funcionario':
            historico_data['id_funcionario'] = user
        elif tipo_usuario == 'aluno':
            historico_data['id_aluno'] = user
        elif tipo_usuario == 'encarregado':
            historico_data['id_encarregado'] = user
        
        HistoricoLogin.objects.create(**historico_data)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except (Funcionario.DoesNotExist, Aluno.DoesNotExist, Encarregado.DoesNotExist):
        return Response(
            {'error': 'Dados Incorrectos'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erro no login: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def logout_view(request):
    """
    Endpoint de logout
    
    Body:
    {
        "user_id": 1,
        "user_type": "funcionario" | "aluno" | "encarregado"
    }
    """
    user_id = request.data.get('user_id')
    user_type = request.data.get('user_type')
    
    try:
        # Atualizar status online
        if user_type == 'funcionario':
            user = Funcionario.objects.get(id_funcionario=user_id)
            user.is_online = False
            user.save()
        elif user_type == 'aluno':
            user = Aluno.objects.get(id_aluno=user_id)
            user.is_online = False
            user.save()
        elif user_type == 'encarregado':
            user = Encarregado.objects.get(id_encarregado=user_id)
            user.is_online = False
            user.save()
        
        # Atualizar histórico de login (hora de saída)
        from django.utils import timezone
        historico = HistoricoLogin.objects.filter(
            **{f'id_{user_type}': user},
            hora_saida__isnull=True
        ).order_by('-hora_entrada').first()
        
        if historico:
            historico.hora_saida = timezone.now()
            historico.save()
        
        return Response(
            {'message': 'Logout realizado com sucesso'},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {'error': f'Erro no logout: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Retorna informações do usuário autenticado baseado no Token JWT.
    A autenticação é tratada pelo SchoolJWTAuthentication configurado no settings.
    """
    try:
        user = request.user
        
        # O user aqui é o objeto retornado pelo SchoolJWTAuthentication.get_user
        # (pode ser Funcionario, Aluno ou Encarregado)
        # (pode ser Funcionario, Aluno ou Encarregado)
        
        if not user:
             return Response(
                {'error': 'Usuário não encontrado ou não autenticado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_type = getattr(request, 'user_type', None)
        
        # Fallback: Detectar tipo pela classe do objeto caso request.user_type falhe
        if not user_type:
            from apis.models import Funcionario, Aluno, Encarregado
            if isinstance(user, Funcionario): user_type = 'funcionario'
            elif isinstance(user, Aluno): user_type = 'aluno'
            elif isinstance(user, Encarregado): user_type = 'encarregado'

        # Verificar se o usuário está inativo (apenas para Alunos e Encarregados)
        if user_type in ['aluno', 'encarregado'] and getattr(user, 'modo_user', None) == 'Inativo':
            return Response(
                {'error': 'A sua conta está inativa. Sessão encerrada.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_data = {}
        
        if user_type == 'funcionario':
            # Verificar restrições de funcionário (Status Activo e Cargo Secretário)
            if user.status_funcionario != 'Activo':
                return Response(
                    {'error': 'A sua conta de funcionário está inativa.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if (user.id_cargo.nome_cargo if user.id_cargo else None) != 'Secretário':
                return Response(
                    {'error': 'Acesso negado. Apenas Secretários podem aceder ao sistema.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            user_data = {
                'id': user.id_funcionario,
                'tipo': 'funcionario',
                'nome': user.nome_completo,
                'email': user.email,
                'cargo': user.id_cargo.nome_cargo if user.id_cargo else None,
                'status': user.status_funcionario,
                'img_path': request.build_absolute_uri(user.img_path.url) if user.img_path else None,
                'is_online': True
            }
        elif user_type == 'aluno':
            from apis.serializers import AlunoDetailSerializer
            
            # Usar serializer detalhado para obter todos os dados do aluno
            serializer = AlunoDetailSerializer(user, context={'request': request})
            user_data = serializer.data
            
            user_data['nome'] = user.nome_completo
            user_data['tipo'] = 'aluno'
            user_data['id'] = user.id_aluno
            user_data['is_online'] = True
            
            # Enriquecer com dados completos de turma, curso e classe
            if user.id_turma:
                turma_detalhes = {
                    'id': user.id_turma.id_turma,
                    'codigo': user.id_turma.codigo_turma,
                    'sala': user.id_turma.id_sala.numero_sala if user.id_turma.id_sala else None,
                    'ano': user.id_turma.ano,
                    'periodo': user.id_turma.id_periodo.periodo if user.id_turma.id_periodo else None,
                }
                
                # Adicionar dados do curso
                if user.id_turma.id_curso:
                    turma_detalhes['curso'] = {
                        'id': user.id_turma.id_curso.id_curso,
                        'nome': user.id_turma.id_curso.nome_curso,
                        'descricao': user.id_turma.id_curso.descricao if hasattr(user.id_turma.id_curso, 'descricao') else None
                    }
                
                # Adicionar dados da classe
                if user.id_turma.id_classe:
                    turma_detalhes['classe'] = {
                        'id': user.id_turma.id_classe.id_classe,
                        'nivel': user.id_turma.id_classe.nivel,
                        'descricao': user.id_turma.id_classe.descricao
                    }
                
                user_data['turma_detalhes'] = turma_detalhes
        elif user_type == 'encarregado':
            user_data = {
                'id': user.id_encarregado,
                'tipo': 'encarregado',
                'nome': user.nome_completo,
                'email': user.email,
                'img_path': request.build_absolute_uri(user.img_path.url) if user.img_path else None,
                'is_online': True
            }
        else:
            return Response(
                {'error': 'Tipo de usuário não identificado'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        return Response({
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Erro ao obter dados do usuário: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['PATCH', 'POST'])
def update_profile_view(request):
    """
    Atualiza informações do perfil e foto do usuário autenticado
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
    try:
        jwt_auth = JWTAuthentication()
        user_auth_tuple = jwt_auth.authenticate(request)
        
        if user_auth_tuple is None:
            return Response({'error': 'Não autorizado'}, status=status.HTTP_401_UNAUTHORIZED)
            
        token = user_auth_tuple[1]
        user_id = token.payload.get('user_id')
        user_type = token.payload.get('user_type')
        
        user = None
        if user_type == 'funcionario':
            user = Funcionario.objects.get(id_funcionario=user_id)
        elif user_type == 'aluno':
            user = Aluno.objects.get(id_aluno=user_id)
        elif user_type == 'encarregado':
            user = Encarregado.objects.get(id_encarregado=user_id)
            
        if not user:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Atualizar campos (apenas email, telefone e imagem permitidos conforme pedido)
        if 'email' in request.data:
            user.email = request.data['email']
        if 'img_path' in request.FILES:
            user.img_path = request.FILES['img_path']
        if 'telefone' in request.data:
            user.telefone = request.data['telefone']
            
        user.save()
        
        # Retornar dados atualizados
        user_data = {
            'id': user_id,
            'tipo': user_type,
            'nome': user.nome_completo,
            'email': user.email,
            'img_path': request.build_absolute_uri(user.img_path.url) if user.img_path else None
        }
        
        return Response({'user': user_data, 'message': 'Perfil atualizado com sucesso'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def change_password_view(request):
    """
    Altera a senha do usuário autenticado
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from django.contrib.auth.hashers import check_password, make_password
    
    try:
        jwt_auth = JWTAuthentication()
        user_auth_tuple = jwt_auth.authenticate(request)
        
        if user_auth_tuple is None:
            return Response({'error': 'Não autorizado'}, status=status.HTTP_401_UNAUTHORIZED)
            
        token = user_auth_tuple[1]
        user_id = token.payload.get('user_id')
        user_type = token.payload.get('user_type')
        
        senha_atual = request.data.get('senha_atual')
        nova_senha = request.data.get('nova_senha')
        
        if not senha_atual or not nova_senha:
            return Response({'error': 'Senha atual e nova senha são obrigatórias'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = None
        if user_type == 'funcionario':
            user = Funcionario.objects.get(id_funcionario=user_id)
        elif user_type == 'aluno':
            user = Aluno.objects.get(id_aluno=user_id)
        elif user_type == 'encarregado':
            user = Encarregado.objects.get(id_encarregado=user_id)
            
        if not user:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        if not check_password(senha_atual, user.senha_hash):
            return Response({'error': 'Senha atual incorreta'}, status=status.HTTP_400_BAD_REQUEST)
            
        user.senha_hash = make_password(nova_senha)
        user.save()
        
        return Response({'message': 'Senha alterada com sucesso'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def verify_password_view(request):
    """
    Verifica se a senha fornecida corresponde à senha do usuário autenticado.
    Usado antes de permitir alterações sensíveis.
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from django.contrib.auth.hashers import check_password
    
    try:
        jwt_auth = JWTAuthentication()
        user_auth_tuple = jwt_auth.authenticate(request)
        
        if user_auth_tuple is None:
            return Response({'error': 'Não autorizado'}, status=status.HTTP_401_UNAUTHORIZED)
            
        token = user_auth_tuple[1]
        user_id = token.payload.get('user_id')
        user_type = token.payload.get('user_type')
        
        senha_atual = request.data.get('senha_atual')
        
        if not senha_atual:
            return Response({'error': 'Senha inválida'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = None
        if user_type == 'funcionario':
            user = Funcionario.objects.get(id_funcionario=user_id)
        elif user_type == 'aluno':
            user = Aluno.objects.get(id_aluno=user_id)
        elif user_type == 'encarregado':
            user = Encarregado.objects.get(id_encarregado=user_id)
            
        if not user:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
            
        if check_password(senha_atual, user.senha_hash):
            return Response({'valid': True, 'message': 'Senha correta'}, status=status.HTTP_200_OK)
        else:
            return Response({'valid': False, 'error': 'Senha incorreta'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Envia um e-mail com link de recuperação de senha
    """
    from django.core.mail import send_mail
    from django.core.signing import Signer, TimestampSigner
    from django.conf import settings
    
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'E-mail é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        
    user = None
    user_type = None
    user_id = None
    
    # Procurar em todas as tabelas
    try:
        user = Funcionario.objects.get(email=email)
        user_type = 'funcionario'
        user_id = user.id_funcionario
    except Funcionario.DoesNotExist:
        try:
            user = Aluno.objects.get(email=email)
            user_type = 'aluno'
            user_id = user.id_aluno
        except Aluno.DoesNotExist:
            try:
                user = Encarregado.objects.get(email=email)
                user_type = 'encarregado'
                user_id = user.id_encarregado
            except Encarregado.DoesNotExist:
                # Retornar sucesso fictício para evitar enumeração de e-mails (segurança)
                return Response({'message': 'Se o e-mail existir no sistema, você receberá um link de recuperação.'})

    # Gerar token assinado com timestamp (expira em 1 hora)
    signer = TimestampSigner()
    token_str = f"{user_type}:{user_id}"
    token = signer.sign(token_str)
    
    # Criar link de reset
    reset_url = f"{settings.SITE_URL}/auth/reset-password?token={token}"
    
    # Mensagem
    subject = "Recuperação de Senha - Instituto Politécnico do Maiombe"
    message = f"""
    Olá {user.nome_completo},
    
    Você solicitou a recuperação de senha da sua conta no sistema do Instituto Politécnico do Maiombe.
    
    Para redefinir sua senha, clique no link abaixo (ou cole no seu navegador):
    {reset_url}
    
    Este link é válido por 1 hora. Se você não solicitou esta alteração, ignore este e-mail.
    
    Atentamente,
    A Equipa de Suporte do IPM
    """
    
    import threading
    def send_email_thread(subject, message, from_email, recipient_list):
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print(f"E-mail de recuperação enviado com sucesso para: {recipient_list}")
        except Exception as e:
            print(f"ERRO CRÍTICO no envio de e-mail (Thread): {str(e)}")

    # Disparar envio em segundo plano (não bloqueia a requisição)
    threading.Thread(
        target=send_email_thread,
        args=(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    ).start()

    return Response({'message': 'Se o e-mail existir no sistema, as instruções foram enviadas. Verifique a sua caixa de entrada.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Valida o token e redefine a senha do usuário
    """
    from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
    from django.contrib.auth.hashers import make_password
    
    token = request.data.get('token')
    nova_senha = request.data.get('nova_senha')
    
    if not token or not nova_senha:
        return Response({'error': 'Token e nova senha são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)
        
    signer = TimestampSigner()
    try:
        # Validar token (max_age = 3600 segundos = 1 hora)
        original_data = signer.unsign(token, max_age=3600)
        user_type, user_id = original_data.split(':')
        
        user = None
        if user_type == 'funcionario':
            user = Funcionario.objects.get(id_funcionario=user_id)
        elif user_type == 'aluno':
            user = Aluno.objects.get(id_aluno=user_id)
        elif user_type == 'encarregado':
            user = Encarregado.objects.get(id_encarregado=user_id)
            
        if not user:
             return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
             
        # Atualizar senha
        user.senha_hash = make_password(nova_senha)
        user.save()
        
        return Response({'message': 'Senha redefinida com sucesso. Já pode fazer login.'})
        
    except SignatureExpired:
        return Response({'error': 'O link de recuperação expirou. Por favor, solicite um novo.'}, status=status.HTTP_400_BAD_REQUEST)
    except (BadSignature, ValueError, Exception) as e:
        return Response({'error': 'Link de recuperação inválido.'}, status=status.HTTP_400_BAD_REQUEST)
