import os
import django
from django.db import connection
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

def force_update():
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'solicitacao_documento';")
        existing_cols = [row[0] for row in cursor.fetchall()]
        
    print(f"Existing columns: {existing_cols}")
    
    with connection.schema_editor() as schema_editor:
        # Check and add canal_pagamento_rup
        if 'canal_pagamento_rup' not in existing_cols:
            print("Adding canal_pagamento_rup...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute('ALTER TABLE solicitacao_documento ADD COLUMN canal_pagamento_rup VARCHAR(20) NULL')
            except Exception as e:
                print(f"Error adding canal_pagamento_rup: {e}")

        if 'data_expiracao_rup' not in existing_cols:
            print("Adding data_expiracao_rup...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute('ALTER TABLE solicitacao_documento ADD COLUMN data_expiracao_rup TIMESTAMP WITH TIME ZONE NULL')
            except Exception as e:
                print(f"Error adding data_expiracao_rup: {e}")

        if 'caminho_arquivo' not in existing_cols:
            print("Adding caminho_arquivo...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute('ALTER TABLE solicitacao_documento ADD COLUMN caminho_arquivo TEXT NULL')
            except Exception as e:
                print(f"Error adding caminho_arquivo: {e}")

        if 'uuid_documento' not in existing_cols:
            print("Adding uuid_documento...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute('ALTER TABLE solicitacao_documento ADD COLUMN uuid_documento UUID NULL')
            except Exception as e:
                print(f"Error adding uuid_documento: {e}")

        if 'data_aprovacao' not in existing_cols:
            print("Adding data_aprovacao...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute('ALTER TABLE solicitacao_documento ADD COLUMN data_aprovacao TIMESTAMP WITH TIME ZONE NULL')
            except Exception as e:
                print(f"Error adding data_aprovacao: {e}")

    print("Update process completed.")

if __name__ == "__main__":
    force_update()
