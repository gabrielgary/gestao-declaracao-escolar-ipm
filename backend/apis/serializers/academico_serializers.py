from rest_framework import serializers
from apis.models import (
    Sala, Classe, Departamento, Seccao, AreaFormacao,
    Curso, Periodo, Turma, Horario,
    MatrizCurricular, MatrizCurricularDisciplina
)


class SalaSerializer(serializers.ModelSerializer):
    """Serializer para Sala"""
    
    class Meta:
        model = Sala
        fields = ['id_sala', 'numero_sala', 'capacidade_alunos', 'criado_em', 'atualizado_em']
        read_only_fields = ['id_sala', 'criado_em', 'atualizado_em']


class ClasseSerializer(serializers.ModelSerializer):
    """Serializer para Classe"""
    
    class Meta:
        model = Classe
        fields = ['id_classe', 'nivel', 'descricao']
        read_only_fields = ['id_classe']


class DepartamentoSerializer(serializers.ModelSerializer):
    """Serializer para Departamento"""
    chefe_nome = serializers.CharField(source='chefe_id_funcionario.nome_completo', read_only=True)
    
    class Meta:
        model = Departamento
        fields = ['id_departamento', 'nome_departamento', 'chefe_id_funcionario', 'chefe_nome']
        read_only_fields = ['id_departamento']


class SeccaoSerializer(serializers.ModelSerializer):
    """Serializer para Seccao"""
    departamento_nome = serializers.CharField(source='id_departamento.nome_departamento', read_only=True)
    
    class Meta:
        model = Seccao
        fields = ['id_seccao', 'nome_seccao', 'id_departamento', 'departamento_nome']
        read_only_fields = ['id_seccao']


class AreaFormacaoSerializer(serializers.ModelSerializer):
    """Serializer para AreaFormacao"""
    responsavel_nome = serializers.CharField(source='id_responsavel.nome_completo', read_only=True)
    
    class Meta:
        model = AreaFormacao
        fields = ['id_area_formacao', 'nome_area', 'id_responsavel', 'responsavel_nome', 'criado_em', 'atualizado_em']
        read_only_fields = ['id_area_formacao', 'criado_em', 'atualizado_em']


class CursoSerializer(serializers.ModelSerializer):
    """Serializer para Curso"""
    area_formacao_nome = serializers.CharField(source='id_area_formacao.nome_area', read_only=True)
    responsavel_nome = serializers.CharField(source='id_responsavel.nome_completo', read_only=True)
    
    class Meta:
        model = Curso
        fields = [
            'id_curso', 'nome_curso', 'id_area_formacao', 'area_formacao_nome',
            'duracao', 'id_responsavel', 'responsavel_nome',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id_curso', 'criado_em', 'atualizado_em']


class CursoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Cursos"""
    area_formacao_nome = serializers.CharField(source='id_area_formacao.nome_area', read_only=True)
    
    class Meta:
        model = Curso
        fields = ['id_curso', 'nome_curso', 'area_formacao_nome', 'duracao']


class PeriodoSerializer(serializers.ModelSerializer):
    """Serializer para Periodo"""
    responsavel_nome = serializers.CharField(source='id_responsavel.nome_completo', read_only=True)
    
    class Meta:
        model = Periodo
        fields = ['id_periodo', 'periodo', 'id_responsavel', 'responsavel_nome']
        read_only_fields = ['id_periodo']


class TurmaSerializer(serializers.ModelSerializer):
    """Serializer para Turma"""
    sala_numero = serializers.IntegerField(source='id_sala.numero_sala', read_only=True)
    curso_nome = serializers.CharField(source='id_curso.nome_curso', read_only=True)
    classe_nivel = serializers.IntegerField(source='id_classe.nivel', read_only=True)
    periodo_nome = serializers.CharField(source='id_periodo.periodo', read_only=True)
    responsavel_nome = serializers.CharField(source='id_responsavel.nome_completo', read_only=True)
    
    class Meta:
        model = Turma
        fields = [
            'id_turma', 'codigo_turma', 'id_sala', 'sala_numero',
            'id_curso', 'curso_nome', 'id_classe', 'classe_nivel',
            'id_periodo', 'periodo_nome', 'id_matriz_curricular', 'ano', 'id_responsavel',
            'responsavel_nome', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id_turma', 'codigo_turma', 'criado_em', 'atualizado_em']


class TurmaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Turmas"""
    curso_nome = serializers.CharField(source='id_curso.nome_curso', read_only=True)
    classe_nivel = serializers.IntegerField(source='id_classe.nivel', read_only=True)
    periodo_nome = serializers.CharField(source='id_periodo.periodo', read_only=True)
    sala_numero = serializers.IntegerField(source='id_sala.numero_sala', read_only=True)
    responsavel_nome = serializers.CharField(source='id_responsavel.nome_completo', read_only=True)
    
    class Meta:
        model = Turma
        fields = [
            'id_turma', 'codigo_turma', 'curso_nome', 'classe_nivel', 
            'periodo_nome', 'ano', 'sala_numero', 'responsavel_nome'
        ]


class HorarioSerializer(serializers.ModelSerializer):
    """Serializer para Horário"""
    disciplina_nome = serializers.CharField(source='id_disciplina.nome', read_only=True)
    professor_nome = serializers.CharField(source='id_professor.nome_completo', read_only=True)
    
    class Meta:
        model = Horario
        fields = [
            'id_horario', 'id_turma', 'id_disciplina', 'disciplina_nome',
            'id_professor', 'professor_nome', 'dia_semana',
            'hora_inicio', 'hora_fim', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id_horario', 'criado_em', 'atualizado_em']
class MatrizCurricularDisciplinaSerializer(serializers.ModelSerializer):
    """Serializer para Disciplina da Matriz"""
    disciplina_nome = serializers.CharField(source='id_disciplina.nome', read_only=True)
    
    class Meta:
        model = MatrizCurricularDisciplina
        fields = [
            'id_matriz_disciplina', 'id_matriz_curricular', 'id_disciplina',
            'disciplina_nome', 'carga_horaria', 'coeficiente', 'e_nuclear'
        ]
        read_only_fields = ['id_matriz_disciplina']


class MatrizCurricularSerializer(serializers.ModelSerializer):
    """Serializer para Matriz Curricular"""
    curso_nome = serializers.CharField(source='id_curso.nome_curso', read_only=True)
    classe_nivel = serializers.IntegerField(source='id_classe.nivel', read_only=True)
    disciplinas = MatrizCurricularDisciplinaSerializer(many=True, read_only=True)
    
    class Meta:
        model = MatrizCurricular
        fields = [
            'id_matriz_curricular', 'id_curso', 'curso_nome',
            'id_classe', 'classe_nivel', 'descricao', 'ano_letivo',
            'ativo', 'disciplinas', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id_matriz_curricular', 'criado_em', 'atualizado_em']
