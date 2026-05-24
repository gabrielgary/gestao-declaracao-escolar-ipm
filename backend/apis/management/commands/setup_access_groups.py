from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apis.models import (
    Nota, FaltaAluno, Turma, Disciplina, Aluno, Matricula, SolicitacaoDocumento
)

class Command(BaseCommand):
    help = 'Configura os grupos de acesso e permissoes iniciais'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando configuracao de grupos...')

        # 1. Grupo Diretores
        diretores, created = Group.objects.get_or_create(name='Diretores')
        if created:
            self.stdout.write('Grupo Diretores criado.')
        else:
            self.stdout.write('Grupo Diretores ja existe.')

        # Diretores geralmente sao superuser, mas se nao forem, podem precisar de permissoes
        # Por enquanto, deixamos vazio pois a premissa e que sao Admin/Superuser

        # 2. Grupo Professores
        professores, created = Group.objects.get_or_create(name='Professores')
        if created:
            self.stdout.write('Grupo Professores criado.')
        
        # Permissoes para Professores
        models_professor_rw = [Nota, FaltaAluno] # Read/Write
        models_professor_ro = [Turma, Disciplina] # Read-Only (Ver turmas e disciplinas)

        perms_professor = []

        # Read/Write permissions
        for model in models_professor_rw:
            ct = ContentType.objects.get_for_model(model)
            p_add = Permission.objects.filter(content_type=ct, codename=f'add_{model._meta.model_name}').first()
            p_change = Permission.objects.filter(content_type=ct, codename=f'change_{model._meta.model_name}').first()
            p_view = Permission.objects.filter(content_type=ct, codename=f'view_{model._meta.model_name}').first()
            
            if p_add: perms_professor.append(p_add)
            if p_change: perms_professor.append(p_change)
            if p_view: perms_professor.append(p_view)

        # Read-Only permissions
        for model in models_professor_ro:
            ct = ContentType.objects.get_for_model(model)
            p_view = Permission.objects.filter(content_type=ct, codename=f'view_{model._meta.model_name}').first()
            if p_view: perms_professor.append(p_view)

        professores.permissions.set(perms_professor)
        self.stdout.write(f'Permissoes atribuidas ao grupo Professores: {len(perms_professor)}')

        # 3. Grupo Secretaria
        secretaria, created = Group.objects.get_or_create(name='Secretaria')
        if created:
            self.stdout.write('Grupo Secretaria criado.')

        # Permissoes para Secretaria
        models_secretaria_rw = [SolicitacaoDocumento]
        models_secretaria_ro = [Aluno, Matricula]

        perms_secretaria = []

        for model in models_secretaria_rw:
            ct = ContentType.objects.get_for_model(model)
            # Full Access on Solicitacoes
            p_add = Permission.objects.filter(content_type=ct, codename=f'add_{model._meta.model_name}').first()
            p_change = Permission.objects.filter(content_type=ct, codename=f'change_{model._meta.model_name}').first()
            p_view = Permission.objects.filter(content_type=ct, codename=f'view_{model._meta.model_name}').first()
            
            if p_add: perms_secretaria.append(p_add)
            if p_change: perms_secretaria.append(p_change)
            if p_view: perms_secretaria.append(p_view)
        
        for model in models_secretaria_ro:
            ct = ContentType.objects.get_for_model(model)
            p_view = Permission.objects.filter(content_type=ct, codename=f'view_{model._meta.model_name}').first()
            if p_view: perms_secretaria.append(p_view)

        # Secretaria tambem pode ver faturas? O plano diz "Remover फाइनेंसiro", mas checkamos status pago...
        # Entao Secretaria precisa ver status da fatura/pagamento pelo menos?
        # A instrucao foi "Sem Financeiro" no frontend, mas backend precisa validar
        # Vou deixar apenas SolicitacaoDocumento por enquanto.

        secretaria.permissions.set(perms_secretaria)
        self.stdout.write(f'Permissoes atribuidas ao grupo Secretaria: {len(perms_secretaria)}')
        
        self.stdout.write(self.style.SUCCESS('Configuracao de grupos concluida com sucesso!'))
