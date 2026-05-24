import os
import django
from django.db import connection, transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

def fix_db():
    print("Starting DB diagnosis...")
    try:
        with connection.cursor() as cursor:
            # Check existing columns
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'solicitacao_documento';")
            existing_cols = [row[0] for row in cursor.fetchall()]
            print(f"Current columns in 'solicitacao_documento': {existing_cols}")

            # Define missing columns to check
            columns_to_add = [
                ('canal_pagamento_rup', 'VARCHAR(20) NULL'),
                ('data_expiracao_rup', 'TIMESTAMP WITH TIME ZONE NULL'),
                ('caminho_arquivo', 'TEXT NULL'),
                ('uuid_documento', 'UUID NULL'),
                ('data_aprovacao', 'TIMESTAMP WITH TIME ZONE NULL'),
            ]

            for col_name, col_def in columns_to_add:
                if col_name not in existing_cols:
                    print(f"Column '{col_name}' is MISSING. Attempting to add...")
                    try:
                        # Postgres requires separate statements usually, but we are in python
                        sql = f"ALTER TABLE solicitacao_documento ADD COLUMN {col_name} {col_def};"
                        cursor.execute(sql)
                        print(f"SUCCESS: Executed {sql}")
                    except Exception as e:
                        print(f"ERROR executing {sql}: {e}")
                else:
                    print(f"Column '{col_name}' ALREADY EXISTS.")

            # Final verification
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'solicitacao_documento';")
            final_cols = [row[0] for row in cursor.fetchall()]
            print(f"Final columns: {final_cols}")

            missing_after_fix = [col[0] for col in columns_to_add if col[0] not in final_cols]
            if missing_after_fix:
                print(f"CRITICAL: The following columns are STILL MISSING: {missing_after_fix}")
            else:
                print("ALL REQUIRED COLUMNS ARE PRESENT.")

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    fix_db()
