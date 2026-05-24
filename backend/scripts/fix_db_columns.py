import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

def fix_columns():
    with connection.cursor() as cursor:
        # Check existing columns
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'solicitacao_documento';")
        existing_columns = [col[0] for col in cursor.fetchall()]
        print("Existing columns:", existing_columns)

        # Add canal_pagamento_rup if missing
        if 'canal_pagamento_rup' not in existing_columns:
            print("Adding column canal_pagamento_rup...")
            cursor.execute("ALTER TABLE solicitacao_documento ADD COLUMN canal_pagamento_rup VARCHAR(20) NULL;")
        
        # Add data_expiracao_rup if missing
        if 'data_expiracao_rup' not in existing_columns:
            print("Adding column data_expiracao_rup...")
            cursor.execute("ALTER TABLE solicitacao_documento ADD COLUMN data_expiracao_rup TIMESTAMP WITH TIME ZONE NULL;")

        # Add caminho_arquivo if missing
        if 'caminho_arquivo' not in existing_columns:
            print("Adding column caminho_arquivo...")
            cursor.execute("ALTER TABLE solicitacao_documento ADD COLUMN caminho_arquivo TEXT NULL;")

        # Add uuid_documento if missing
        if 'uuid_documento' not in existing_columns:
            print("Adding column uuid_documento...")
            cursor.execute("ALTER TABLE solicitacao_documento ADD COLUMN uuid_documento UUID NULL;")

        # Add data_aprovacao if missing
        if 'data_aprovacao' not in existing_columns:
            print("Adding column data_aprovacao...")
            cursor.execute("ALTER TABLE solicitacao_documento ADD COLUMN data_aprovacao TIMESTAMP WITH TIME ZONE NULL;")

        print("Finished checking and adding columns.")

if __name__ == "__main__":
    fix_columns()
