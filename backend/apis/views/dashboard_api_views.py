from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, Case, When, IntegerField
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from apis.models import Aluno, SolicitacaoDocumento, Fatura, Nota, Turma, HistoricoLogin
from apis.serializers.documento_serializers import SolicitacaoDocumentoListSerializer

class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Definição dos períodos (Mês atual vs Mês anterior, ou 30 dias)
        agora = timezone.now()
        trinta_dias_atras = agora - timedelta(days=30)
        sessenta_dias_atras = agora - timedelta(days=60)

        # --- 1. KPIs ---
        
        # 1.1 Total Solicitações
        total_solicitacoes = SolicitacaoDocumento.objects.count() # Total geral
        # Para percentual: (novos últimos 30 dias vs penúltimos 30 dias)
        solicitacoes_atual = SolicitacaoDocumento.objects.filter(data_solicitacao__gte=trinta_dias_atras).count()
        solicitacoes_anterior = SolicitacaoDocumento.objects.filter(
            data_solicitacao__gte=sessenta_dias_atras, 
            data_solicitacao__lt=trinta_dias_atras
        ).count()

        # 1.2 Declarações Emitidas (Tudo que não está pendente ou rejeitado é considerado "em processamento/emitido")
        STATUS_EFETIVOS = ['pago', 'aguardando_assinatura', 'impresso', 'disponivel']
        
        declaracoes_emitidas = SolicitacaoDocumento.objects.filter(status_solicitacao__in=STATUS_EFETIVOS).count()
        declaracoes_atual = SolicitacaoDocumento.objects.filter(
            status_solicitacao__in=STATUS_EFETIVOS, 
            data_solicitacao__gte=trinta_dias_atras
        ).count()
        declaracoes_anterior = SolicitacaoDocumento.objects.filter(
            status_solicitacao__in=STATUS_EFETIVOS, 
            data_solicitacao__gte=sessenta_dias_atras, 
            data_solicitacao__lt=trinta_dias_atras
        ).count()

        # 1.3 Novos Alunos
        novos_alunos_total = Aluno.objects.count()
        novos_alunos_atual = Aluno.objects.filter(criado_em__gte=trinta_dias_atras).count()
        novos_alunos_anterior = Aluno.objects.filter(
            criado_em__gte=sessenta_dias_atras, 
            criado_em__lt=trinta_dias_atras
        ).count()

        # 1.4 Receita (Apenas solicitações que foram pagas/confirmadas)
        # Excluímos 'pendente' (não pago) e 'rejeitado' (cancelado)
        receita_total = SolicitacaoDocumento.objects.filter(
            status_solicitacao__in=STATUS_EFETIVOS
        ).aggregate(total=Sum('valor_rupe'))['total'] or 0
        
        receita_atual = SolicitacaoDocumento.objects.filter(
            status_solicitacao__in=STATUS_EFETIVOS, 
            data_solicitacao__gte=trinta_dias_atras
        ).aggregate(total=Sum('valor_rupe'))['total'] or 0
        
        receita_anterior = SolicitacaoDocumento.objects.filter(
            status_solicitacao__in=STATUS_EFETIVOS, 
            data_solicitacao__gte=sessenta_dias_atras, 
            data_solicitacao__lt=trinta_dias_atras
        ).aggregate(total=Sum('valor_rupe'))['total'] or 0

        # --- 2. Dados de Engajamento (Setor/Pie Chart) ---
        # Total de logins únicos ou total de acessos por tipo de usuário
        # Aqui vamos contar o total de logins registrados no histórico GLOBAL (ou últimos 6 meses se preferir filtrar)
        
        # Opcional: Filtro de últimos 6 meses para o gráfico de setor refletir relevância recente
        seis_meses_atras = agora - timedelta(days=180)
        
        alunos_logins = HistoricoLogin.objects.filter(
            id_aluno__isnull=False, 
            hora_entrada__gte=seis_meses_atras
        ).count()
        
        funcionarios_logins = HistoricoLogin.objects.filter(
            id_funcionario__isnull=False, 
            hora_entrada__gte=seis_meses_atras
        ).count()
        
        encarregados_logins = HistoricoLogin.objects.filter(
            id_encarregado__isnull=False, 
            hora_entrada__gte=seis_meses_atras
        ).count()

        engagement_data = [
            {'name': 'Alunos', 'value': alunos_logins},
            {'name': 'Funcionários', 'value': funcionarios_logins},
            {'name': 'Encarregados', 'value': encarregados_logins},
        ]

        # --- 3. Comparação de Solicitações (Otimizado) ---
        # Usar agregação para reduzir queries (de 18+ para 1)
        start_date = agora - timedelta(days=180)
        
        stats = SolicitacaoDocumento.objects.filter(
            data_solicitacao__gte=start_date
        ).annotate(
            month=TruncMonth('data_solicitacao')
        ).values('month').annotate(
            Declaracao=Count('id_solicitacao', filter=Q(tipo_documento__icontains='Declaração')),
            Certificado=Count('id_solicitacao', filter=Q(tipo_documento__icontains='Certificado')),
            Boletim=Count('id_solicitacao', filter=Q(tipo_documento__icontains='Boletim'))
        ).order_by('month')

        # Dicionário auxiliar para preencher meses vazios
        stats_dict = {
            s['month'].strftime('%Y-%m'): s 
            for s in stats if s['month']
        }

        requests_comparison_data = []
        for i in range(5, -1, -1):
            date = agora - timedelta(days=i*30)
            key = date.strftime('%Y-%m')
            month_name = date.strftime('%b')
            
            data = stats_dict.get(key, {
                'Declaracao': 0,
                'Certificado': 0,
                'Boletim': 0
            })
            
            requests_comparison_data.append({
                'name': month_name,
                'Declaracao': data['Declaracao'],
                'Certificado': data['Certificado'],
                'Boletim': data['Boletim']
            })

        recent_solicitacoes = SolicitacaoDocumento.objects.select_related(
            'id_aluno'
        ).all().order_by('-data_solicitacao')[:5]
        serializer = SolicitacaoDocumentoListSerializer(recent_solicitacoes, many=True, context={'request': request})

        # 5. Auditoria Recente
        from apis.models import Historico
        audit_logs = Historico.objects.select_related('id_funcionario', 'id_aluno').order_by('-data_hora')[:5]
        audit_data = [
            {
                'id': h.id_historico,
                'user': h.id_funcionario.nome_completo if h.id_funcionario else h.id_aluno.nome_completo if h.id_aluno else 'Sistema',
                'action': h.tipo_accao,
                'time': h.data_hora
            } for h in audit_logs
        ]

        return Response({
            'kpis': {
                'total_solicitacoes': {
                    'total': total_solicitacoes,
                    'current': solicitacoes_atual,
                    'previous': solicitacoes_anterior
                },
                'declaracoes_emitidas': {
                    'total': declaracoes_emitidas,
                    'current': declaracoes_atual,
                    'previous': declaracoes_anterior
                },
                'novos_alunos': {
                    'total': novos_alunos_total,
                    'current': novos_alunos_atual,
                    'previous': novos_alunos_anterior
                },
                'receita_total': {
                    'total': float(receita_total),
                    'current': float(receita_atual),
                    'previous': float(receita_anterior)
                }
            },
            'engagement_data': engagement_data,
            'requests_comparison_data': requests_comparison_data,
            'recent_activities': serializer.data,
            'recent_audit_logs': audit_data
        })
