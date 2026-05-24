# Importar todas as views para facilitar o uso
from .auth_views import login_view, logout_view, me_view, update_profile_view, change_password_view, verify_password_view, forgot_password_view, reset_password_view
from .usuario_views import (
    CargoViewSet, FuncionarioViewSet, EncarregadoViewSet, CargoFuncionarioViewSet
)
from .aluno_views import AlunoViewSet, AlunoEncarregadoViewSet
from .academico_views import (
    SalaViewSet, ClasseViewSet, DepartamentoViewSet, SeccaoViewSet,
    AreaFormacaoViewSet, CursoViewSet, PeriodoViewSet, TurmaViewSet,
    MatrizCurricularViewSet, MatrizCurricularDisciplinaViewSet
)
from .avaliacao_views import (
    TipoDisciplinaViewSet, DisciplinaViewSet,
    ProfessorDisciplinaViewSet, NotaViewSet, FaltaAlunoViewSet
)
from .documento_views import DocumentoViewSet, SolicitacaoDocumentoViewSet
from .biblioteca_views import CategoriaViewSet, LivroViewSet
from .financeiro_views import FaturaViewSet, PagamentoViewSet
from .auditoria_views import HistoricoLoginViewSet, HistoricoViewSet
from .notificacao_views import NotificacaoViewSet
from .backup_views import BackupViewSet, ConfiguracaoSistemaViewSet
from .dashboard_api_views import DashboardStatsAPIView
from .report_views import ReportViewSet
from .report_data_views import ReportDataViewSet

__all__ = [
    # Auth
    'login_view', 'logout_view', 'me_view', 'update_profile_view', 'change_password_view', 'verify_password_view',
    'forgot_password_view', 'reset_password_view',
    # Usuários
    'CargoViewSet', 'FuncionarioViewSet', 'EncarregadoViewSet', 'CargoFuncionarioViewSet',
    # Alunos
    'AlunoViewSet', 'AlunoEncarregadoViewSet',
    # Acadêmico
    'SalaViewSet', 'ClasseViewSet', 'DepartamentoViewSet', 'SeccaoViewSet',
    'AreaFormacaoViewSet', 'CursoViewSet', 'PeriodoViewSet', 'TurmaViewSet',
    'MatrizCurricularViewSet', 'MatrizCurricularDisciplinaViewSet',
    # Avaliações
    'TipoDisciplinaViewSet', 'DisciplinaViewSet', 
    'ProfessorDisciplinaViewSet', 'NotaViewSet', 'FaltaAlunoViewSet',
    # Documentos
    'DocumentoViewSet', 'SolicitacaoDocumentoViewSet',
    # Biblioteca
    'CategoriaViewSet', 'LivroViewSet',
    # Financeiro
    'FaturaViewSet', 'PagamentoViewSet',
    'HistoricoLoginViewSet',
    'HistoricoViewSet',
    'BackupViewSet', 'ConfiguracaoSistemaViewSet',
    'DashboardStatsAPIView',
    'NotificacaoViewSet',
    'ReportViewSet',
    'ReportDataViewSet',
]
