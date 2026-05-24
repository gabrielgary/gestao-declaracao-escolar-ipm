import os
import django
import psycopg2
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def add_column():
    db_config = settings.DATABASES['default']
    try:
        conn = psycopg2.connect(
            dbname=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            host=db_config['HOST'],
            port=db_config['PORT']
        )
        cur = conn.cursor()
        
        # Tentar adicionar a coluna
        try:
            cur.execute("ALTER TABLE configuracao_sistema ADD COLUMN director_geral varchar(150);")
            conn.commit()
            print("Coluna 'director_geral' adicionada com sucesso!")
        except Exception as e:
            conn.rollback()
            if "already exists" in str(e):
                print("A coluna já existe.")
            else:
                print(f"Erro ao adicionar coluna: {e}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    add_column()
