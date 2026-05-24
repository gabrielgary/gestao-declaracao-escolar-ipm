import os
import django
import sys
from io import StringIO

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Mock de configurações de banco de dados para usar SQLite
import django.conf
from django.conf import settings

# Redefinir DATABASES para SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Criar uma classe de Mock para as configurações
class SettingsMock:
    def __init__(self, original_settings):
        self._original = original_settings
    def __getattr__(self, name):
        if name == 'DATABASES':
            return DATABASES
        return getattr(self._original, name)

try:
    # Gambiarra para sobrescrever settings ANTES do django.setup()
    django.setup()
    
    # Sobrescrevendo após setup para garantir que comandos usem o mock
    from django.conf import settings
    settings.DATABASES = DATABASES

    from django.core.management import call_command

    out = StringIO()
    
    # Gerar SQL para a migração inicial
    print("Gerando SQL para apis 0001 (SQLite Dialect)...")
    call_command('sqlmigrate', 'apis', '0001', stdout=out)
    sql_0001 = out.getvalue()
    
    out = StringIO()
    print("Gerando SQL para apis 0002 (SQLite Dialect)...")
    call_command('sqlmigrate', 'apis', '0002', stdout=out)
    sql_0002 = out.getvalue()
    
    schema_file = '../docs/db_schema.sql'
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write("-- Esquema do Banco de Dados (Dialeto SQLite para referência de estrutura)\n")
        f.write("-- Gerado a partir das migrações do Django\n\n")
        f.write(sql_0001)
        f.write("\n\n")
        f.write(sql_0002)
    
    print(f"Sucesso! Esquema salvo em {schema_file}")

except Exception as e:
    import traceback
    print(f"Erro ao gerar esquema: {str(e)}")
    traceback.print_exc()
