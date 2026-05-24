from django.db import models
from .base import BaseModel
from .usuarios import Funcionario
import datetime

class Sala(BaseModel):
    """Salas de aula"""
    id_sala = models.AutoField(primary_key=True)
    numero_sala = models.SmallIntegerField(verbose_name='Número da Sala')
    capacidade_alunos = models.IntegerField(verbose_name='Capacidade')
    localizacao=models.CharField(max_length=50, verbose_name="Localização", blank=True, null=True)
    
    class Meta:
        db_table = 'sala'
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['numero_sala']
    
    def __str__(self):
        return f"Sala {self.numero_sala}"


class Classe(models.Model):
    """Níveis/Anos escolares"""
    id_classe = models.AutoField(primary_key=True)
    nivel = models.SmallIntegerField(verbose_name='Nível')
    descricao = models.CharField(max_length=80, null=True, blank=True)
    
    class Meta:
        db_table = 'classe'
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['nivel']
    
    def __str__(self):
        return f"{self.nivel}ª Classe"


class Departamento(models.Model):
    """Departamentos da instituição"""
    id_departamento = models.AutoField(primary_key=True)
    nome_departamento = models.CharField(max_length=150, verbose_name='Nome do Departamento')
    chefe_id_funcionario = models.ForeignKey(
        Funcionario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='departamentos_chefiados',
        verbose_name='Chefe'
    )
    
    class Meta:
        db_table = 'departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nome_departamento']
    
    def __str__(self):
        return self.nome_departamento


class Seccao(models.Model):
    """Seções dentro dos departamentos"""
    id_seccao = models.AutoField(primary_key=True)
    nome_seccao = models.CharField(max_length=150, verbose_name='Nome da Seção')
    id_departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Departamento'
    )
    
    class Meta:
        db_table = 'seccao'
        verbose_name = 'Seção'
        verbose_name_plural = 'Seções'
        ordering = ['nome_seccao']
    
    def __str__(self):
        return self.nome_seccao


class AreaFormacao(BaseModel):
    """Áreas de formação dos cursos"""
    id_area_formacao = models.AutoField(primary_key=True)
    nome_area = models.CharField(max_length=150, verbose_name='Nome da Área')
    id_responsavel = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='areas_coordenadas',
        verbose_name='Responsável'
    )
    
    class Meta:
        db_table = 'area_formacao'
        verbose_name = 'Área de Formação'
        verbose_name_plural = 'Áreas de Formação'
        ordering = ['nome_area']
    
    def __str__(self):
        return self.nome_area


class Curso(BaseModel):
    """Cursos oferecidos"""
    id_curso = models.AutoField(primary_key=True)
    nome_curso = models.CharField(max_length=150, verbose_name='Nome do Curso')
    id_area_formacao = models.ForeignKey(
        AreaFormacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Área de Formação'
    )
    duracao = models.IntegerField(null=True, blank=True, verbose_name='Duração (Anos)',default=4)
    id_responsavel = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cursos_coordenados',
        verbose_name='Coordenador'
    )
    
    class Meta:
        db_table = 'curso'
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nome_curso']
    
    def __str__(self):
        return self.nome_curso


class Periodo(models.Model):
    """Períodos de aula (Manhã, Tarde, Noite)"""
    
    PERIODO_CHOICES = [
        ('Manhã', 'Manhã'),
        ('Tarde', 'Tarde'),
        ('Noite', 'Noite'),
    ]
    
    id_periodo = models.AutoField(primary_key=True)
    periodo = models.CharField(max_length=10, choices=PERIODO_CHOICES,unique=True)
    id_responsavel = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='periodos_responsaveis',
        verbose_name='Responsável'
    )
    
    class Meta:
        db_table = 'periodo'
        verbose_name = 'Período'
        verbose_name_plural = 'Períodos'
    
    def __str__(self):
        return self.periodo


def current_year():
    return str(datetime.date.today().year)


class MatrizCurricular(BaseModel):
    """Matriz Curricular (Plano de Estudos)"""
    id_matriz_curricular = models.AutoField(primary_key=True)
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name='Curso')
    id_classe = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name='Classe')
    descricao = models.CharField(max_length=150, verbose_name='Descrição (ex: Grade 2024)', blank=True, null=True)
    ano_letivo = models.CharField(max_length=20, blank=True, null=True, verbose_name='Ano Letivo')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        db_table = 'matriz_curricular'
        verbose_name = 'Matriz Curricular'
        verbose_name_plural = 'Matrizes Curriculares'
        unique_together = ['id_curso', 'id_classe', 'ano_letivo']

    def __str__(self):
        return f"{self.id_curso} - {self.id_classe} ({self.descricao or 'Padrão'})"


class MatrizCurricularDisciplina(models.Model):
    """Disciplinas da Matriz Curricular"""
    id_matriz_disciplina = models.AutoField(primary_key=True)
    id_matriz_curricular = models.ForeignKey(MatrizCurricular, on_delete=models.CASCADE, related_name='disciplinas', verbose_name='Matriz')
    id_disciplina = models.ForeignKey('Disciplina', on_delete=models.CASCADE, verbose_name='Disciplina')
    carga_horaria = models.IntegerField(default=0, verbose_name='Carga Horária Semanal')
    coeficiente = models.DecimalField(max_digits=4, decimal_places=2, default=1.00, verbose_name='Coeficiente/Peso')
    e_nuclear = models.BooleanField(default=True, verbose_name='É Nuclear?')

    class Meta:
        db_table = 'matriz_curricular_disciplina'
        verbose_name = 'Disciplina da Matriz'
        verbose_name_plural = 'Disciplinas da Matriz'
        unique_together = ['id_matriz_curricular', 'id_disciplina']

    def __str__(self):
        return f"{self.id_disciplina} (Matriz: {self.id_matriz_curricular.id_curso})"


class Turma(BaseModel):
    """Turmas de alunos"""
    id_turma = models.AutoField(primary_key=True)
    id_sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Sala')
    id_curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Curso')
    id_classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Classe')
    id_periodo = models.ForeignKey(Periodo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Período')
    id_matriz_curricular = models.ForeignKey(MatrizCurricular, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Matriz Curricular')
    
    # Campos mantidos para compatibilidade (serão preenchidos via Matriz)
    ano = models.CharField(max_length=4, null=True, blank=True, verbose_name='Ano', default=current_year)
    codigo_turma = models.CharField(max_length=50, unique=True, blank=True, verbose_name='Código da Turma')
    id_responsavel = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='turmas_responsaveis',
        verbose_name='Responsável'
    )
    
    class Meta:
        db_table = 'turma'
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['codigo_turma']
    
    def save(self, *args, **kwargs):
        # Auto-preencher Curso e Classe se Matriz estiver definida
        if self.id_matriz_curricular:
            self.id_curso = self.id_matriz_curricular.id_curso
            self.id_classe = self.id_matriz_curricular.id_classe

        if self.id_sala and self.id_curso and self.id_classe and self.id_periodo and self.ano:
            sala = str(self.id_sala.numero_sala)
            curso = self.id_curso.nome_curso[:2].upper()
            classe = str(self.id_classe.nivel)
            periodo = self.id_periodo.periodo[0].upper()
            ano = str(self.ano)[-2:]
            
            self.codigo_turma = f"{sala}{curso}{classe}{periodo}{ano}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo_turma



class Horario(BaseModel):
    """Horário das aulas (Timetable)"""
    
    DIA_SEMANA_CHOICES = [
        ('Segunda-feira', 'Segunda-feira'),
        ('Terça-feira', 'Terça-feira'),
        ('Quarta-feira', 'Quarta-feira'),
        ('Quinta-feira', 'Quinta-feira'),
        ('Sexta-feira', 'Sexta-feira'),
        ('Sábado', 'Sábado'),
    ]
    
    id_horario = models.AutoField(primary_key=True)
    id_turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name='Turma', related_name='horarios')
    id_disciplina = models.ForeignKey('Disciplina', on_delete=models.CASCADE, verbose_name='Disciplina')
    id_professor = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Professor')
    dia_semana = models.CharField(max_length=20, choices=DIA_SEMANA_CHOICES, verbose_name='Dia da Semana')
    hora_inicio = models.TimeField(verbose_name='Hora de Início')
    hora_fim = models.TimeField(verbose_name='Hora de Fim')
    
    class Meta:
        db_table = 'horario'
        verbose_name = 'Horário'
        verbose_name_plural = 'Horários'
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.id_turma.codigo_turma} - {self.dia_semana} ({self.hora_inicio}-{self.hora_fim})"
