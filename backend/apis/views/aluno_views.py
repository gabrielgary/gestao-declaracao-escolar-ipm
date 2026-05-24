from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apis.models import Aluno, AlunoEncarregado
from apis.serializers import (
    AlunoSerializer, AlunoListSerializer, AlunoDetailSerializer,
    AlunoEncarregadoSerializer
)


class AlunoViewSet(viewsets.ModelViewSet):
    """ViewSet para Aluno"""
    queryset = Aluno.objects.select_related('id_turma').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    #filterset_fields = ['status_aluno', 'id_turma', 'genero']
    search_fields = ['nome_completo', 'email', 'numero_matricula', 'numero_bi']
    ordering_fields = ['nome_completo', 'numero_matricula', 'criado_em']
    ordering = ['nome_completo']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AlunoDetailSerializer
        elif self.action == 'list':
            return AlunoListSerializer
        return AlunoSerializer
    
    @action(detail=False, methods=['get'])
    def ativos(self, request):
        """Retorna apenas alunos ativos"""
        alunos = self.queryset.filter(status_aluno='Activo')
        serializer = AlunoListSerializer(alunos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def notas(self, request, pk=None):
        """Retorna notas do aluno"""
        from apis.models import Nota
        from apis.serializers import NotaListSerializer
        
        aluno = self.get_object()
        notas = Nota.objects.filter(id_aluno=aluno).select_related(
            'id_disciplina', 'id_professor'
        ).order_by('-data_lancamento')
        serializer = NotaListSerializer(notas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def faltas(self, request, pk=None):
        """Retorna faltas do aluno"""
        from apis.models import FaltaAluno
        from apis.serializers import FaltaAlunoListSerializer
        
        aluno = self.get_object()
        faltas = FaltaAluno.objects.filter(id_aluno=aluno).select_related(
            'id_disciplina', 'id_turma'
        ).order_by('-data_falta')
        serializer = FaltaAlunoListSerializer(faltas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def boletim(self, request, pk=None):
        """Retorna boletim completo do aluno com estatísticas"""
        from apis.models import Nota, FaltaAluno
        from django.db.models import Avg, Count
        
        aluno = self.get_object()
        
        # Notas agrupadas por disciplina
        notas_por_disciplina = Nota.objects.filter(
            id_aluno=aluno
        ).values(
            'id_disciplina__id_disciplina',
            'id_disciplina__nome'
        ).annotate(
            media=Avg('valor'),
            total_avaliacoes=Count('id_nota')
        )
        
        # Média Geral
        media_geral = Nota.objects.filter(id_aluno=aluno).aggregate(Avg('valor'))['valor__avg'] or 0
        
        # Faltas totais
        total_faltas = FaltaAluno.objects.filter(id_aluno=aluno).count()
        faltas_justificadas = FaltaAluno.objects.filter(
            id_aluno=aluno, justificada=True
        ).count()
        
        # Cálculo de presença (aproximado)
        # Vamos assumir 200 aulas por ano para simplicidade ou calcular baseado em disciplinas
        presenca_percentual = 100
        if total_faltas > 0:
            # Lógica simples para demonstração
            presenca_percentual = max(0, 100 - (total_faltas * 0.5)) 

        # Faltas agrupadas por disciplina
        faltas_por_disciplina = FaltaAluno.objects.filter(
            id_aluno=aluno
        ).values(
            'id_disciplina__nome'
        ).annotate(
            total=Count('id_falta')
        )
        
        # Calcular notas detalhadas usando AcademicService
        from apis.services.academic_service import AcademicService
        notas_list = AcademicService.get_boletim_aluno(aluno)
        
        # Mapear faltas para as disciplinas das notas
        faltas_map = {f['id_disciplina__nome']: f['total'] for f in faltas_por_disciplina}
        
        for nota in notas_list:
            nota['faltas'] = faltas_map.get(nota['disciplina'], 0)
            # Assumindo 40 aulas por disciplina para o cálculo de percentagem ou usar carga horária da matriz se disponível
            # Aqui estamos simplificando
            nota['presenca_percentual'] = max(0, 100 - (nota['faltas'] * 2.5))

        return Response({
            'aluno': AlunoDetailSerializer(aluno).data,
            'notas_por_disciplina': notas_list,
            'media_geral': round(float(media_geral), 1),
            'presenca_percentual': round(presenca_percentual, 1),
            'total_faltas': total_faltas,
            'faltas_justificadas': faltas_justificadas,
            'faltas_injustificadas': total_faltas - faltas_justificadas
        })

    @action(detail=True, methods=['get'])
    def horario(self, request, pk=None):
        """Retorna o horário semanal da turma do aluno"""
        from apis.models import Horario
        from apis.serializers import HorarioSerializer
        
        aluno = self.get_object()
        if not aluno.id_turma:
            return Response({'error': 'Aluno não está vinculado a nenhuma turma'}, status=status.HTTP_404_NOT_FOUND)
            
        horarios = Horario.objects.filter(id_turma=aluno.id_turma).select_related(
            'id_disciplina', 'id_professor'
        )
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Exporta lista de alunos em formato CSV"""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type='text/csv')
        filename = f"alunos_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Nome Completo', 'Email', 'Número BI', 'Matrícula', 
            'Gênero', 'Status', 'Turma', 'Data Criação'
        ])

        alunos = self.filter_queryset(self.get_queryset())
        for aluno in alunos:
            writer.writerow([
                aluno.id_aluno,
                aluno.nome_completo,
                aluno.email or '',
                aluno.numero_bi or '',
                aluno.numero_matricula or '',
                aluno.get_genero_display() if aluno.genero else '',
                aluno.status_aluno,
                aluno.id_turma.codigo_turma if aluno.id_turma else 'Sem Turma',
                aluno.criado_em.strftime('%Y-%m-%d %H:%M')
            ])

        return response
    
    @action(detail=True, methods=['get'])
    def encarregados(self, request, pk=None):
        """Retorna encarregados do aluno"""
        from apis.serializers import EncarregadoListSerializer
        
        aluno = self.get_object()
        vinculos = AlunoEncarregado.objects.filter(
            id_aluno=aluno
        ).select_related('id_encarregado')
        encarregados = [v.id_encarregado for v in vinculos]
        serializer = EncarregadoListSerializer(encarregados, many=True)
        return Response(serializer.data)


class AlunoEncarregadoViewSet(viewsets.ModelViewSet):
    """ViewSet para AlunoEncarregado"""
    queryset = AlunoEncarregado.objects.select_related(
        'id_aluno', 'id_encarregado'
    ).all()
    serializer_class = AlunoEncarregadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    #filterset_fields = ['id_aluno', 'id_encarregado']
