from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Cria usuario para a Secretaria'

    def handle(self, *args, **kwargs):
        username = 'secretaria_api'
        email = 'secretaria@escola.com'
        password = 'SecretariaPassword123!'

        try:
            if User.objects.filter(username=username).exists():
                self.stdout.write(f'Usuario {username} ja existe.')
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                self.stdout.write(f'Usuario {username} criado com sucesso.')

            # Adicionar ao grupo Secretaria
            grupo_secretaria = Group.objects.filter(name='Secretaria').first()
            if grupo_secretaria:
                user.groups.add(grupo_secretaria)
                self.stdout.write(f'Usuario {username} adicionado ao grupo Secretaria.')
            else:
                self.stdout.write(self.style.WARNING('Grupo Secretaria nao encontrado! Rode setup_access_groups primeiro.'))
            
            # Garantir que nao e staff/superuser, apenas API user?
            # Se for apenas API, is_staff=False. Se precisar acessar Admin, is_staff=True.
            # O plano diz "Frontend da Secretaria". Entao API user.
            user.is_staff = False 
            user.is_superuser = False
            user.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar usuario: {e}'))
