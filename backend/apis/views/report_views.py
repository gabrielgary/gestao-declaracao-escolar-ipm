import csv
from io import BytesIO
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Sum

from apis.models import (
    SolicitacaoDocumento, Aluno, Funcionario, 
    Historico, HistoricoLogin, Fatura, ConfiguracaoSistema, Turma
)
from apis.services.pdf_service import PDFService
from apis.services.report_service import ReportService

class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet para geração de relatórios em PDF e CSV
    """
    permission_classes = [IsAuthenticated]

    def _generate_csv_response(self, filename, headers, data):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)
        return response

    def _generate_pdf_response(self, template_name, context, filename):
        config = ConfiguracaoSistema.objects.first()
        context['config'] = config
        pdf_content = PDFService.render_to_pdf(template_name, context)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        return response

    @action(detail=False, methods=['get'])
    def solicitacoes(self, request):
        """Relatório de solicitações de documentos"""
        format_type = request.query_params.get('format', 'pdf')
        status_filter = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = SolicitacaoDocumento.objects.select_related('id_aluno', 'id_funcionario').all()
        if status_filter:
            queryset = queryset.filter(status_solicitacao=status_filter)
        if start_date:
            queryset = queryset.filter(data_solicitacao__gte=start_date)
        if end_date:
            queryset = queryset.filter(data_solicitacao__lte=end_date)
        
        if format_type == 'json':
            # Para previsualização
            return Response([
                {
                    'id': s.id_solicitacao,
                    'aluno': s.id_aluno.nome_completo,
                    'tipo': s.tipo_documento,
                    'data': s.data_solicitacao.strftime('%d/%m/%Y'),
                    'status': s.status_solicitacao,
                    'valor': s.valor_rupe
                } for s in queryset[:20] # Limitar preview
            ])

        if format_type == 'csv':
            headers = ['ID', 'Aluno', 'Tipo', 'Data', 'Status', 'Valor']
            data = [
                [
                    s.id_solicitacao, 
                    s.id_aluno.nome_completo, 
                    s.tipo_documento, 
                    s.data_solicitacao.strftime('%d/%m/%Y'), 
                    s.status_solicitacao, 
                    s.valor_rupe
                ] for s in queryset
            ]
            return self._generate_csv_response('relatorio_solicitacoes', headers, data)
        
        context = {
            'title': 'Relatório de Solicitações de Documentos',
            'data': queryset,
            'hoje': timezone.now(),
            'user': request.user
        }
        return self._generate_pdf_response('pdf/report_solicitacoes.html', context, 'relatorio_solicitacoes')

    @action(detail=False, methods=['get'])
    def alunos(self, request):
        """Relatório de alunos"""
        format_type = request.query_params.get('format', 'pdf')
        turma_id = request.query_params.get('turma')
        classe_id = request.query_params.get('classe')
        
        queryset = Aluno.objects.select_related('id_turma', 'id_turma__id_classe').all()
        if turma_id:
            queryset = queryset.filter(id_turma_id=turma_id)
        if classe_id:
            queryset = queryset.filter(id_turma__id_classe_id=classe_id)
            
        if format_type == 'json':
            return Response([
                {
                    'id': a.id_aluno,
                    'nome': a.nome_completo,
                    'genero': a.genero,
                    'turma': a.id_turma.codigo_turma if a.id_turma else 'N/A',
                    'classe': f"{a.id_turma.id_classe.nivel}ª" if a.id_turma and a.id_turma.id_classe else 'N/A'
                } for a in queryset[:20]
            ])

        if format_type == 'csv':
            headers = ['ID', 'Nome Completo', 'Gênero', 'Turma', 'Classe']
            data = [
                [
                    a.id_aluno, 
                    a.nome_completo, 
                    a.genero, 
                    a.id_turma.codigo_turma if a.id_turma else 'N/A',
                    a.id_turma.id_classe.nivel if a.id_turma and a.id_turma.id_classe else 'N/A'
                ] for a in queryset
            ]
            return self._generate_csv_response('relatorio_alunos', headers, data)
            
        context = {
            'title': 'Relatório de Alunos',
            'data': queryset,
            'hoje': timezone.now(),
            'user': request.user
        }
        return self._generate_pdf_response('pdf/report_alunos.html', context, 'relatorio_alunos')

    @action(detail=False, methods=['get'])
    def funcionarios(self, request):
        """Relatório de funcionários"""
        format_type = request.query_params.get('format', 'pdf')
        queryset = Funcionario.objects.select_related('id_cargo').all()
        
        if format_type == 'json':
            return Response([
                {
                    'id': f.id_funcionario,
                    'nome': f.nome_completo,
                    'cargo': f.id_cargo.nome_cargo if f.id_cargo else 'N/A',
                    'telefone': f.telefone,
                    'status': f.status_funcionario
                } for f in queryset[:20]
            ])

        if format_type == 'csv':
            headers = ['ID', 'Nome Completo', 'Cargo', 'Telefone', 'Email']
            data = [
                [
                    f.id_funcionario, 
                    f.nome_completo, 
                    f.id_cargo.nome_cargo if f.id_cargo else 'N/A',
                    f.telefone,
                    f.email
                ] for f in queryset
            ]
            return self._generate_csv_response('relatorio_funcionarios', headers, data)
            
        context = {
            'title': 'Relatório de Funcionários',
            'data': queryset,
            'hoje': timezone.now(),
            'user': request.user
        }
        return self._generate_pdf_response('pdf/report_funcionarios.html', context, 'relatorio_funcionarios')

    @action(detail=False, methods=['get'])
    def mensal(self, request):
        """Relatório mensal de documentos (boletins, certificados, declaracoes)"""
        format_type = request.query_params.get('format', 'pdf')
        month = request.query_params.get('mes', timezone.now().month)
        year = request.query_params.get('ano', timezone.now().year)
        
        # Em um sistema real, aqui você filtraria por faturas ou documentos emitidos
        # Exemplo simplificado usando Fatura
        stats = []
        for doc_type in ['Boletim', 'Certificado', 'Declaração']:
            count = SolicitacaoDocumento.objects.filter(
                tipo_documento=doc_type,
                data_solicitacao__month=month,
                data_solicitacao__year=year
            ).count()
            total_value = SolicitacaoDocumento.objects.filter(
                tipo_documento=doc_type,
                data_solicitacao__month=month,
                data_solicitacao__year=year
            ).aggregate(Sum('valor_rupe'))['valor_rupe__sum'] or 0
            stats.append({
                'tipo': doc_type,
                'quantidade': count,
                'total': total_value
            })
            
        if format_type == 'json':
            return Response(stats)

        # Original queryset for CSV/PDF (if needed, but the new 'stats' logic replaces it for these formats too)
        # The original code used `queryset = SolicitacaoDocumento.objects.filter(...)`
        # For consistency with the new 'stats' logic, we'll use 'stats' for CSV as well.
        
        if format_type == 'csv':
            headers = ['Tipo de Documento', 'Quantidade', 'Valor Total']
            data = [[item['tipo'], item['quantidade'], item['total']] for item in stats]
            return self._generate_csv_response(f'relatorio_mensal_{month}_{year}', headers, data)
            
        context = {
            'title': f'Relatório Mensal - {month}/{year}',
            'stats': stats, # Use the calculated stats
            'mes': month,
            'ano': year,
            'hoje': timezone.now(),
            'user': request.user
        }
        return self._generate_pdf_response('pdf/report_mensal.html', context, f'relatorio_mensal_{month}_{year}')

    @action(detail=False, methods=['get'])
    def auditoria(self, request):
        """Relatório de auditoria (histórico e login)"""
        format_type = request.query_params.get('format', 'pdf')
        audit_type = request.query_params.get('tipo', 'historico') # historico ou login
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if audit_type == 'login':
            queryset = HistoricoLogin.objects.all()
            if start_date:
                queryset = queryset.filter(hora_entrada__gte=start_date)
            if end_date:
                queryset = queryset.filter(hora_entrada__lte=end_date)
            
            if format_type == 'json':
                return Response([
                    {
                        'usuario': (h.id_funcionario.nome_completo if h.id_funcionario else 
                                    h.id_aluno.nome_completo if h.id_aluno else 
                                    h.id_encarregado.nome_completo if h.id_encarregado else 'Sistema'),
                        'tipo_usuario': 'Funcionario' if h.id_funcionario else 'Aluno' if h.id_aluno else 'Encarregado',
                        'ip': h.ip_usuario,
                        'entrada': h.hora_entrada.strftime('%d/%m/%Y %H:%M:%S'),
                        'saida': h.hora_saida.strftime('%d/%m/%Y %H:%M:%S') if h.hora_saida else 'Ativo'
                    } for h in queryset[:20]
                ])

            if format_type == 'csv':
                headers = ['Usuário', 'Tipo', 'IP', 'Entrada', 'Saída']
                data = [
                    [
                        (l.id_funcionario.nome_completo if l.id_funcionario else 
                         l.id_aluno.nome_completo if l.id_aluno else 
                         l.id_encarregado.nome_completo if l.id_encarregado else 'Sistema'),
                        'Funcionario' if l.id_funcionario else 'Aluno' if l.id_aluno else 'Encarregado',
                        l.ip_usuario,
                        l.hora_entrada.strftime('%d/%m/%Y %H:%M:%S'),
                        l.hora_saida.strftime('%d/%m/%Y %H:%M:%S') if l.hora_saida else 'Ativo'
                    ] for l in queryset
                ]
                return self._generate_csv_response('relatorio_auditoria_login', headers, data)
            template = 'pdf/report_auditoria_login.html'
        else:
            queryset = Historico.objects.select_related('id_funcionario', 'id_aluno').all()[:100]
            if format_type == 'json':
                return Response([
                    {
                        'usuario': h.id_funcionario.nome_completo if h.id_funcionario else h.id_aluno.nome_completo if h.id_aluno else 'Sistema',
                        'tipo_usuario': 'Ação do Sistema',
                        'entrada': h.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                        'saida': h.tipo_accao
                    } for h in queryset
                ])
                
            if format_type == 'csv':
                headers = ['Usuário', 'Ação', 'Data/Hora', 'Detalhes Antigos', 'Detalhes Novos']
                data = [
                    [
                        (h.id_funcionario.nome_completo if h.id_funcionario else h.id_aluno.nome_completo if h.id_aluno else 'Sistema'),
                        h.tipo_accao,
                        h.data_hora.strftime('%d/%m/%Y %H:%M:%S'),
                        str(h.dados_anteriores),
                        str(h.dados_novos)
                    ] for h in queryset
                ]
                return self._generate_csv_response('relatorio_auditoria_sistema', headers, data)
            template = 'pdf/report_auditoria_sistema.html'
            
        context = {
            'title': f'Relatório de Auditoria - {audit_type.capitalize()}',
            'logs': queryset,
            'hoje': timezone.now(),
            'user': request.user
        }
        return self._generate_pdf_response(f'pdf/report_auditoria_{audit_type}.html', context, f'auditoria_{audit_type}')
