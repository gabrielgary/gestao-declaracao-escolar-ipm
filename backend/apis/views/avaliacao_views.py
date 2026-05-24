from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from apis.permissions.custom_permissions import IsProfessor, IsDirecao, IsFuncionario
from apis.services.academic_service import AcademicService

from apis.models import (
    TipoDisciplina, Disciplina,
    ProfessorDisciplina, Nota, FaltaAluno
)
from apis.serializers import (
    TipoDisciplinaSerializer, DisciplinaSerializer, DisciplinaListSerializer,
    ProfessorDisciplinaSerializer,
    NotaSerializer, NotaListSerializer, NotaLancamentoLoteSerializer,
    FaltaAlunoSerializer, FaltaAlunoListSerializer
)


class TipoDisciplinaViewSet(viewsets.ModelViewSet):
    """ViewSet para TipoDisciplina"""
    queryset = TipoDisciplina.objects.all()
    serializer_class = TipoDisciplinaSerializer
    permission_classes = [IsAuthenticated]


class DisciplinaViewSet(viewsets.ModelViewSet):
    """ViewSet para Disciplina"""
    queryset = Disciplina.objects.select_related(
        'id_tipo_disciplina', 'id_coordenador'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    #filterset_fields = ['id_tipo_disciplina']
    search_fields = ['nome']
    ordering_fields = ['nome', 'carga_horaria']
    ordering = ['nome']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DisciplinaListSerializer
        return DisciplinaSerializer




class ProfessorDisciplinaViewSet(viewsets.ModelViewSet):
    """ViewSet para ProfessorDisciplina"""
    queryset = ProfessorDisciplina.objects.select_related(
        'id_funcionario', 'id_disciplina', 'id_turma'
    ).all()
    serializer_class = ProfessorDisciplinaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    #filterset_fields = ['id_funcionario', 'id_disciplina', 'id_turma']


class NotaViewSet(viewsets.ModelViewSet):
    """ViewSet para Nota"""
    queryset = Nota.objects.select_related(
        'id_aluno', 'id_disciplina', 'id_professor', 'id_turma'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    #filterset_fields = ['id_aluno', 'id_disciplina', 'id_turma', 'tipo_avaliacao']
    ordering_fields = ['data_lancamento', 'valor']
    ordering = ['-data_lancamento']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotaListSerializer
        elif self.action == 'lancar_lote':
            return NotaLancamentoLoteSerializer
        return NotaSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[IsProfessor | IsDirecao])
    def lancar_lote(self, request):
        """Lançamento de notas em lote"""
        serializer = NotaLancamentoLoteSerializer(data=request.data)
        if serializer.is_valid():
            id_turma = serializer.validated_data['id_turma']
            id_disciplina = serializer.validated_data.get('id_disciplina')
            id_matriz_disciplina = serializer.validated_data.get('id_matriz_disciplina')
            id_professor = serializer.validated_data['id_professor']
            trimestre = serializer.validated_data['trimestre']
            tipo_nota = serializer.validated_data['tipo_nota']
            notas_data = serializer.validated_data['notas']
            
            try:
                from apis.models import Nota, Aluno, Disciplina, Funcionario, Turma, MatrizCurricularDisciplina
                
                turma = Turma.objects.get(id_turma=id_turma)
                professor = Funcionario.objects.get(id_funcionario=id_professor)
                
                # Resolvendo disciplina
                if id_matriz_disciplina:
                    matriz_disciplina = MatrizCurricularDisciplina.objects.get(id_matriz_curricular_disciplina=id_matriz_disciplina)
                    disciplina = matriz_disciplina.id_disciplina
                else:
                    matriz_disciplina = None
                    disciplina = Disciplina.objects.get(id_disciplina=id_disciplina)

                notas_processadas = 0
                for n in notas_data:
                    # Update or Create
                    nota_obj, created = Nota.objects.update_or_create(
                        id_aluno_id=n['id_aluno'],
                        id_turma=turma,
                        id_disciplina=disciplina,
                        trimestre=trimestre,
                        tipo_nota=tipo_nota,
                        defaults={
                            'id_professor': professor,
                            'valor': n['valor']
                        }
                    )
                    notas_processadas += 1
                
                return Response({
                    'message': f'{notas_processadas} notas processadas (lançadas/atualizadas).',
                    'count': notas_processadas
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FaltaAlunoViewSet(viewsets.ModelViewSet):
    """ViewSet para FaltaAluno"""
    queryset = FaltaAluno.objects.select_related(
        'id_aluno', 'id_disciplina', 'id_turma'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    #filterset_fields = ['id_aluno', 'id_disciplina', 'id_turma', 'justificada']
    ordering_fields = ['data_falta']
    ordering = ['-data_falta']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FaltaAlunoListSerializer
        return FaltaAlunoSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[IsProfessor | IsDirecao])
    def registrar_lote(self, request):
        """Registro de faltas em lote usando AcademicService"""
        aluno_ids = request.data.get('aluno_ids', [])
        disciplina_id = request.data.get('disciplina_id')
        turma_id = request.data.get('turma_id')
        data_falta = request.data.get('data_falta')
        observacao = request.data.get('observacao')
        
        try:
            total = AcademicService.registrar_falta_lote(
                aluno_ids, disciplina_id, turma_id, data_falta, observacao
            )
            return Response({
                'message': f'{total} faltas registradas com sucesso',
                'count': total
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
