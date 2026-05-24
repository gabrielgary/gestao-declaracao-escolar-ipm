import os
import sys
import django
import random
from datetime import date, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apis.models import Aluno, Turma, Classe

def generate_angolan_phone():
    prefixes = ['92', '93', '94', '99', '91', '95']
    prefix = random.choice(prefixes)
    suffixes = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefix}{suffixes}"

def generate_bi():
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return f"{random.randint(100000000, 999999999)}{random.choice(letters)}{random.choice(letters)}{random.randint(100, 999)}"

def populate_10th_grade_students():
    print("🚀 Iniciando população de 20 alunos na 10ª Classe...")
    
    # Busca a 10ª Classe
    try:
        decima_classe = Classe.objects.get(nivel="10")
    except Classe.DoesNotExist:
        print("❌ 10ª Classe não encontrada no sistema. Abortando.")
        return

    # Busca ou cria uma Turma para a 10ª Classe
    turma_10, created = Turma.objects.get_or_create(
        codigo_turma="10A",
        id_classe=decima_classe,
        defaults={
            'turno': 'Manhã',
            'ano': str(date.today().year),
            'sala': 'Sala 10'
        }
    )
    if created:
         print(f"✅ Criada nova turma {turma_10.codigo_turma} para a 10ª Classe.")

    first_names_m = ["João", "Pedro", "Manuel", "António", "Carlos", "José", "Paulo", "Rui", "Miguel", "Bruno"]
    first_names_f = ["Maria", "Ana", "Sofia", "Isabel", "Marta", "Joana", "Catarina", "Rita", "Inês", "Beatriz"]
    last_names = ["Silva", "Santos", "Costa", "Pereira", "Fernandes", "Gomes", "Martins", "Lopes", "Almeida", "Ribeiro"]
    
    count = 0
    for i in range(1, 21):
        genero = random.choice(['M', 'F'])
        
        if genero == 'M':
            nome = f"{random.choice(first_names_m)} {random.choice(last_names)}"
        else:
            nome = f"{random.choice(first_names_f)} {random.choice(last_names)}"
            
        matricula = f"MAT{date.today().year}10A{str(i).zfill(3)}"
        email = f"aluno.{matricula.lower()}@ipm.co.ao"
        
        # Gera data de nascimento entre 15 e 18 anos atrás
        days_old = random.randint(15 * 365, 18 * 365)
        nascimento = date.today() - timedelta(days=days_old)
        
        bi_gerado = generate_bi()
        
        try:
            aluno = Aluno.objects.create(
                nome_completo=nome,
                numero_bi=bi_gerado,
                email=email,
                numero_matricula=matricula,
                telefone=generate_angolan_phone(),
                genero=genero,
                data_nascimento=nascimento,
                provincia_residencia="Luanda",
                municipio_residencia="Luanda",
                status_aluno='Activo',
                id_turma=turma_10,
                senha_hash=bi_gerado  # A senha base será o BI para eles fazerem login 
            )
            count += 1
            print(f"✅ [{count}/20] Cadastrado: {aluno.nome_completo} ({aluno.numero_matricula})")
        except Exception as e:

            print(f"⚠️ Erro ao cadastrar aluno {nome}: {e}")

    print(f"\n🎉 Sucesso! {count} alunos inseridos na turma {turma_10.codigo_turma} ({decima_classe.nivel}ª Classe).")

if __name__ == "__main__":
    populate_10th_grade_students()
