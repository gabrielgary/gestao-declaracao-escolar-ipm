"""
URLs da API v1
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from apis.serializers.auth_serializers import SchoolTokenRefreshSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = SchoolTokenRefreshSerializer

from apis.views import (
    # Auth views
    login_view, logout_view, me_view, update_profile_view, change_password_view, verify_password_view,
    forgot_password_view, reset_password_view,
    # ViewSets
    CargoViewSet, FuncionarioViewSet, EncarregadoViewSet, CargoFuncionarioViewSet,
    AlunoViewSet, AlunoEncarregadoViewSet, NotificacaoViewSet,
    SalaViewSet, ClasseViewSet, DepartamentoViewSet, SeccaoViewSet,
    AreaFormacaoViewSet, CursoViewSet, PeriodoViewSet, TurmaViewSet,
    TipoDisciplinaViewSet, DisciplinaViewSet,
    ProfessorDisciplinaViewSet, NotaViewSet, FaltaAlunoViewSet,
    DocumentoViewSet, SolicitacaoDocumentoViewSet,
    CategoriaViewSet, LivroViewSet,
    FaturaViewSet, PagamentoViewSet,
    HistoricoLoginViewSet, HistoricoViewSet, BackupViewSet, ConfiguracaoSistemaViewSet,
    DashboardStatsAPIView,
    MatrizCurricularViewSet, MatrizCurricularDisciplinaViewSet,
    ReportViewSet,
    ReportDataViewSet
)

# Criar router e registrar ViewSets
router = DefaultRouter()

# Usuários
router.register(r'cargos', CargoViewSet, basename='cargo')
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionario')
router.register(r'encarregados', EncarregadoViewSet, basename='encarregado')
router.register(r'cargo-funcionario', CargoFuncionarioViewSet, basename='cargo-funcionario')

# Alunos
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'aluno-encarregado', AlunoEncarregadoViewSet, basename='aluno-encarregado')

# Acadêmico
router.register(r'salas', SalaViewSet, basename='sala')
router.register(r'classes', ClasseViewSet, basename='classe')
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'seccoes', SeccaoViewSet, basename='seccao')
router.register(r'areas-formacao', AreaFormacaoViewSet, basename='area-formacao')
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'periodos', PeriodoViewSet, basename='periodo')
router.register(r'turmas', TurmaViewSet, basename='turma')
router.register(r'matrizes-curriculares', MatrizCurricularViewSet, basename='matriz-curricular')
router.register(r'matriz-disciplinas', MatrizCurricularDisciplinaViewSet, basename='matriz-disciplina')

# Avaliações
router.register(r'tipos-disciplina', TipoDisciplinaViewSet, basename='tipo-disciplina')
router.register(r'disciplinas', DisciplinaViewSet, basename='disciplina')
router.register(r'professor-disciplina', ProfessorDisciplinaViewSet, basename='professor-disciplina')
router.register(r'notas', NotaViewSet, basename='nota')
router.register(r'faltas', FaltaAlunoViewSet, basename='falta')

# Documentos
router.register(r'documentos', DocumentoViewSet, basename='documento')
router.register(r'solicitacoes', SolicitacaoDocumentoViewSet, basename='solicitacao')

# Biblioteca
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'livros', LivroViewSet, basename='livro')

# Financeiro
router.register(r'faturas', FaturaViewSet, basename='fatura')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')
router.register(r'historico-login', HistoricoLoginViewSet, basename='historico-login')
router.register(r'historico', HistoricoViewSet, basename='historico')
router.register(r'backups', BackupViewSet, basename='backup')
router.register(r'configuracao-sistema', ConfiguracaoSistemaViewSet, basename='configuracao-sistema')
router.register(r'reports', ReportViewSet, basename='report')

# Dados Brutos para Relatórios (Frontend Filtering)
urlpatterns_reports = [
    path('reports/data/solicitacoes/', ReportDataViewSet.as_view({'get': 'list_solicitacoes'}), name='report-data-solicitacoes'),
    path('reports/data/alunos/', ReportDataViewSet.as_view({'get': 'list_alunos'}), name='report-data-alunos'),
    path('reports/data/funcionarios/', ReportDataViewSet.as_view({'get': 'list_funcionarios'}), name='report-data-funcionarios'),
    path('reports/data/auditoria/', ReportDataViewSet.as_view({'get': 'list_auditoria'}), name='report-data-auditoria'),
    path('reports/data/logins/', ReportDataViewSet.as_view({'get': 'list_logins'}), name='report-data-logins'),
    path('reports/config/', ReportDataViewSet.as_view({'get': 'get_config'}), name='report-config'),
]


# URLs
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacoes')

urlpatterns = [
    # Autenticação
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', me_view, name='me'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/update-profile/', update_profile_view, name='update-profile'),
    path('auth/change-password/', change_password_view, name='change-password'),
    path('auth/verify-password/', verify_password_view, name='verify-password'),
    path('auth/forgot-password/', forgot_password_view, name='forgot-password'),
    path('auth/reset-password/', reset_password_view, name='reset-password'),
    
    # Dashboard
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
    
    # Relatórios
    path('', include(urlpatterns_reports)),
    
    # Incluir rotas do router
    path('', include(router.urls)),
]
