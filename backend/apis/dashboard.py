import json
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncMonth
from apis.models import (
    Aluno, Funcionario, Turma, Curso, SolicitacaoDocumento, Fatura, Nota, HistoricoLogin
)
import datetime

def dashboard_callback(request, context):
    """
    Callback para popular o dashboard do Django Unfold.
    """
    try:
        agora = timezone.now()
        seis_meses_atras = agora - datetime.timedelta(days=180)

        # =====================================================================
        # 1. KPIs (Resumo Executivo)
        # =====================================================================
        total_alunos_ativos = Aluno.objects.filter(status_aluno='Activo').count()
        
        # Financeiro: Balanço de Faturas
        faturas_pagas = Fatura.objects.filter(status='paga').aggregate(total=Sum('total'))['total'] or 0
        faturas_pendentes = Fatura.objects.filter(status='pendente').aggregate(total=Sum('total'))['total'] or 0
        taxa_inadimplencia = (faturas_pendentes / (faturas_pagas + faturas_pendentes) * 100) if (faturas_pagas + faturas_pendentes) > 0 else 0
        
        # Acadêmico: Performance
        media_geral = Nota.objects.filter(valor__isnull=False).aggregate(media=Avg('valor'))['media'] or 0
        solicitacoes_pendentes = SolicitacaoDocumento.objects.filter(status_solicitacao='pendente').count()

        kpis = [
            {
                'title': 'Comunidade Escolar',
                'metric': f"{total_alunos_ativos}",
                'footer': 'Alunos Activos no Sistema',
                'icon': 'groups',
                'color': 'primary',
            },
            {
                'title': 'Saúde Financeira',
                'metric': f"{faturas_pagas:,.0f} Kz",
                'footer': f"Receita Confirmada",
                'icon': 'account_balance_wallet',
                'color': 'success',
            },
            {
                'title': 'Inadimplência',
                'metric': f"{taxa_inadimplencia:.1f}%",
                'footer': f"{faturas_pendentes:,.0f} Kz Pendentes",
                'icon': 'trending_down',
                'color': 'danger' if taxa_inadimplencia > 20 else 'warning',
            },
            {
                'title': 'Pedidos Pendentes',
                'metric': f"{solicitacoes_pendentes}",
                'footer': 'Solicitações de Documentos',
                'icon': 'pending_actions',
                'color': 'info',
            },
        ]

        # =====================================================================
        # 2. GRÁFICOS (Inteligência de Dados)
        # =====================================================================
        
        # A. Tendência de Matrículas (Linha - 6 meses)
        matriculas_mes = Aluno.objects.filter(criado_em__gte=seis_meses_atras) \
            .annotate(month=TruncMonth('criado_em')) \
            .values('month') \
            .annotate(total=Count('id_aluno')) \
            .order_by('month')
        
        line_labels = [m['month'].strftime('%b/%Y') for m in matriculas_mes if m['month']]
        line_data = [m['total'] for m in matriculas_mes if m['month']]

        enrollment_chart = {
            "labels": line_labels if line_labels else ["Sem dados"],
            "datasets": [{
                "label": "Novas Matrículas",
                "data": line_data if line_data else [0],
                "borderColor": "#10b981",
                "backgroundColor": "rgba(16, 185, 129, 0.1)",
                "fill": True,
                "tension": 0.4,
            }]
        }

        # B. Saúde Financeira: Pago vs Pendente (Barras Comparativas)
        fin_stats = Fatura.objects.filter(status__in=['paga', 'pendente']) \
            .annotate(month=TruncMonth('criado_em')) \
            .values('month', 'status') \
            .annotate(total=Sum('total')) \
            .order_by('month')
        
        # Organizar dados para o gráfico de barras
        months_list = sorted(list(set([fs['month'].strftime('%b/%Y') for fs in fin_stats if fs['month']])))
        if not months_list: months_list = ["N/A"]
        
        pago_data = []
        pendente_data = []
        
        for m in months_list:
            v_pago = sum(item['total'] for item in fin_stats if item['month'] and item['month'].strftime('%b/%Y') == m and item['status'] == 'paga')
            v_pendente = sum(item['total'] for item in fin_stats if item['month'] and item['month'].strftime('%b/%Y') == m and item['status'] == 'pendente')
            pago_data.append(float(v_pago))
            pendente_data.append(float(v_pendente))

        finance_chart = {
            "labels": months_list,
            "datasets": [
                {
                    "label": "Receita Recebida",
                    "data": pago_data,
                    "backgroundColor": "#10b981",
                    "borderRadius": 5,
                },
                {
                    "label": "Receita Pendente",
                    "data": pendente_data,
                    "backgroundColor": "#f43f5e",
                    "borderRadius": 5,
                }
            ]
        }

        # C. Distribuição Académica (Doughnut - Alunos por Curso)
        cursos_data = Aluno.objects.values('id_turma__id_curso__nome_curso') \
            .annotate(total=Count('id_aluno')) \
            .order_by('-total')[:5] # Top 5 cursos
            
        pie_labels = [c['id_turma__id_curso__nome_curso'] or "Sem Curso" for c in cursos_data]
        pie_values = [c['total'] for c in cursos_data]

        academic_chart = {
            "labels": pie_labels if pie_labels else ["Nenhum Aluno"],
            "datasets": [{
                "data": pie_values if pie_values else [100],
                "backgroundColor": ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899"],
                "borderWidth": 0,
            }]
        }

        # D. Actividade de Acessos (Linha - Últimos 15 dias)
        from django.db.models.functions import TruncDay
        quinze_dias_atras = agora - datetime.timedelta(days=15)
        logins_dia = HistoricoLogin.objects.filter(hora_entrada__gte=quinze_dias_atras) \
            .annotate(day=TruncDay('hora_entrada')) \
            .values('day') \
            .annotate(total=Count('id_historico_login')) \
            .order_by('day')
        
        login_labels = [l['day'].strftime('%d/%m') for l in logins_dia if l['day']]
        login_values = [l['total'] for l in logins_dia if l['day']]

        activity_chart = {
            "labels": login_labels if login_labels else ["Sem dados"],
            "datasets": [{
                "label": "Acessos Diários",
                "data": login_values if login_values else [0],
                "borderColor": "#3b82f6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "fill": True,
                "tension": 0.4,
            }]
        }

        # E. Status das Solicitações (Doughnut - Pipeline)
        status_data = SolicitacaoDocumento.objects.values('status_solicitacao') \
            .annotate(total=Count('id_solicitacao'))
            
        status_labels = [dict(SolicitacaoDocumento.STATUS_CHOICES).get(s['status_solicitacao'], s['status_solicitacao']) for s in status_data]
        status_values = [s['total'] for s in status_data]

        status_chart = {
            "labels": status_labels if status_labels else ["Nenhuma"],
            "datasets": [{
                "data": status_values if status_values else [100],
                "backgroundColor": ["#f59e0b", "#10b981", "#3b82f6", "#8b5cf6", "#ec4899", "#f43f5e"],
                "borderWidth": 0,
            }]
        }

        # F. Distribuição por Gênero (Doughnut - Demografia)
        genero_data = Aluno.objects.values('genero').annotate(total=Count('id_aluno'))
        gen_labels = [g['genero'] or "Não especificado" for g in genero_data]
        gen_values = [g['total'] for g in genero_data]

        gender_chart = {
            "labels": gen_labels if gen_labels else ["Sem dados"],
            "datasets": [{
                "data": gen_values if gen_values else [0],
                "backgroundColor": ["#3b82f6", "#ec4899", "#94a3b8"],
                "borderWidth": 0,
            }]
        }

        charts = [
            {
                "title": "Fluxo de Caixa Mensal (Kz)",
                "type": "bar",
                "json_data": json.dumps(finance_chart)
            },
            {
                "title": "Crescimento de Matrículas",
                "type": "line",
                "json_data": json.dumps(enrollment_chart)
            },
            {
                "title": "Volume de Acessos (15 dias)",
                "type": "line",
                "json_data": json.dumps(activity_chart)
            },
            {
                "title": "Status das Solicitações",
                "type": "doughnut",
                "json_data": json.dumps(status_chart)
            },
            {
                "title": "Distribuição por Cursos (TOP 5)",
                "type": "doughnut",
                "json_data": json.dumps(academic_chart)
            },
            {
                "title": "Demografia por Gênero",
                "type": "doughnut",
                "json_data": json.dumps(gender_chart)
            }
        ]

        context.update({
            "kpis": kpis,
            "charts": charts
        })

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro no Dashboard Admin: {str(e)}")
        context.update({"kpis": [], "charts": []})

    return context
