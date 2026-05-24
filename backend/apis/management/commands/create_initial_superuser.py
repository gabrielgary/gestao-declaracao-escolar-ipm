from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Cria um superusuario inicial (Diretor)'

    def handle(self, *args, **kwargs):
        username = 'director'
        email = 'director@escola.com'
        password = 'DirectorPass123!'

        try:
            if User.objects.filter(username=username).exists():
                self.stdout.write(f'Superusuario {username} ja existe.')
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(f'Superusuario {username} criado com sucesso.')

            # Adicionar ao grupo Diretores
            grupo_diretores = Group.objects.filter(name='Diretores').first()
            if grupo_diretores:
                user.groups.add(grupo_diretores)
                self.stdout.write(f'Superusuario {username} adicionado ao grupo Diretores.')
            else:
                self.stdout.write(self.style.WARNING('Grupo Diretores nao encontrado! Rode setup_access_groups primeiro.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar superusuario: {e}'))
