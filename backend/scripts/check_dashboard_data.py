from apis.models import Aluno, Nota, Funcionario
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
import datetime
from django.utils import timezone

print("=== CHECKING DATA FOR DASHBOARD ===")

# 1. Alunos por Curso
print("\n[1] Alunos por Curso:")
alunos_por_curso = Aluno.objects.values('id_turma__id_curso__nome_curso').annotate(total=Count('id_aluno')).order_by('-total')
count = 0
for item in alunos_por_curso:
    print(f" - {item['id_turma__id_curso__nome_curso']}: {item['total']}")
    count += 1
if count == 0:
    print(" -> NENHUM DADO ENCONTRADO (Alunos sem turma ou curso?)")

# 2. Gênero
print("\n[2] Gênero:")
alunos_por_genero = Aluno.objects.values('genero').annotate(total=Count('id_aluno'))
for item in alunos_por_genero:
    print(f" - {item['genero']}: {item['total']}")

# 3. Notas (Timeline)
print("\n[3] Notas (Últimos 180 dias):")
last_6_months = timezone.now() - datetime.timedelta(days=180)
notas = Nota.objects.filter(data_lancamento__gte=last_6_months).count()
print(f" -> Total Notas Recentes: {notas}")
if notas == 0:
    total_notas = Nota.objects.count()
    print(f" -> Total Notas no DB (qualquer data): {total_notas}")
    if total_notas > 0:
        latest = Nota.objects.order_by('-data_lancamento').first()
        print(f" -> Última nota lançada em: {latest.data_lancamento if latest else 'N/A'}")

print("\n=== END ===")
