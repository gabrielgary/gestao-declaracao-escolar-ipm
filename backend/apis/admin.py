from django.contrib import admin
from django.db.models import Count, Avg, Sum, Q
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action

from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from apis.views.admin_views import GradeLaunchView, GradeLaunch13View

from apis.models import (
    # Usuários
    Cargo, Funcionario, Encarregado, CargoFuncionario,
    # Alunos
    Aluno, AlunoEncarregado,
    # Acadêmico
    Sala, Classe, Departamento, Seccao, AreaFormacao, Curso, Periodo, Turma, MatrizCurricular, MatrizCurricularDisciplina,
    # Avaliações
    TipoDisciplina, Disciplina,  ProfessorDisciplina, Nota, FaltaAluno,
    # Documentos
    Documento, SolicitacaoDocumento,
    # Biblioteca
    Categoria, Livro,
    # Financeiro
    Fatura, Pagamento,
    # Matrículas
    Inscricao, Matricula,
    # Auditoria
    Historico, HistoricoLogin, Notificacao, ConfiguracaoSistema
)


# =============================================================================
# 1. ACADÊMICO E ESTRUTURA
# =============================================================================

@admin.register(Sala)
class SalaAdmin(ModelAdmin):
    list_display = ['numero_sala', 'capacidade_alunos']
    search_fields = ['numero_sala']
    list_filter = []

@admin.register(Classe)
class ClasseAdmin(ModelAdmin):
    list_display = ['nivel', 'descricao', 'total_alunos']
    search_fields = ['descricao']
    
    @display(description='Total Alunos')
    def total_alunos(self, obj):
        count = Aluno.objects.filter(id_turma__id_classe=obj).count()
        return format_html('<span class="badge badge-info">{}</span>', count)

@admin.register(Departamento)
class DepartamentoAdmin(ModelAdmin):
    list_display = ['nome_departamento', 'chefe_id_funcionario']
    search_fields = ['nome_departamento', 'chefe_id_funcionario__nome_completo']
    autocomplete_fields = ['chefe_id_funcionario']

@admin.register(Seccao)
class SeccaoAdmin(ModelAdmin):
    list_display = ['nome_seccao', 'departamento_badge']
    search_fields = ['nome_seccao']
    list_filter = ['id_departamento']
    autocomplete_fields = ['id_departamento']

    @display(description='Departamento', ordering='id_departamento__nome_departamento')
    def departamento_badge(self, obj):
        if obj.id_departamento:
            return obj.id_departamento.nome_departamento
        return '-'

@admin.register(AreaFormacao)
class AreaFormacaoAdmin(ModelAdmin):
    list_display = ['nome_area', 'id_responsavel', 'total_cursos']
    search_fields = ['nome_area', 'id_responsavel__nome_completo']
    autocomplete_fields = ['id_responsavel']

    @display(description='Cursos')
    def total_cursos(self, obj):
        count = Curso.objects.filter(id_area_formacao=obj).count()
        return format_html('<span class="badge badge-primary">{}</span>', count)

@admin.register(Periodo)
class PeriodoAdmin(ModelAdmin):
    list_display = ['periodo']
    search_fields = ['periodo']

# =============================================================================
# 2. USUÁRIOS E ASSOCIAÇÕES
# =============================================================================

@admin.register(Cargo)
class CargoAdmin(ModelAdmin):
    list_display = ['nome_cargo', 'total_funcionarios', 'criado_em']
    search_fields = ['nome_cargo']
    
    @display(description='Funcionários')
    def total_funcionarios(self, obj):
        count = Funcionario.objects.filter(id_cargo=obj).count()
        return format_html('<span class="badge badge-info">{}</span>', count)

@admin.register(Funcionario)
class FuncionarioAdmin(ModelAdmin):
    list_display = ['img_path_display', 'nome_completo', 'cargo_badge', 'status_badge', 'online_badge']
    list_filter = ['status_funcionario', 'id_cargo', 'genero', 'is_online']
    search_fields = ['nome_completo', 'email', 'codigo_identificacao']
    list_per_page = 20
    
    @display(description='Foto')
    def img_path_display(self, obj):
        if obj.img_path:
             return format_html('<img src="{}" width="30" height="30" style="border-radius:50%;" />', obj.img_path.url)
        return '-'

    @display(description='Cargo', ordering='id_cargo__nome_cargo')
    def cargo_badge(self, obj):
        if obj.id_cargo:
            return format_html('<span class="badge badge-primary">{}</span>', obj.id_cargo.nome_cargo)
        return '-'
    
    @display(description='Status', ordering='status_funcionario')
    def status_badge(self, obj):
        colors = {'Activo': 'success', 'Inactivo': 'warning', 'Demitido': 'danger'}
        color = colors.get(obj.status_funcionario, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status_funcionario)
    
    @display(description='Online', boolean=True)
    def online_badge(self, obj):
        return obj.is_online

@admin.register(Aluno)
class AlunoAdmin(ModelAdmin):
    list_display = ['img_path_display', 'nome_completo', 'numero_matricula', 'turma_badge', 'status_badge', 'online_badge']
    list_filter = ['status_aluno', 'id_turma__id_curso', 'id_turma__id_classe', 'genero']
    search_fields = ['nome_completo', 'numero_matricula', 'numero_bi']
    autocomplete_fields = ['id_turma']
    list_per_page = 20

    @display(description='Foto')
    def img_path_display(self, obj):
         if obj.img_path:
             return format_html('<img src="{}" width="30" height="30" style="border-radius:50%;" />', obj.img_path.url)
         return '-'

    @display(description='Turma', ordering='id_turma__codigo_turma')
    def turma_badge(self, obj):
        if obj.id_turma:
            return format_html('<span class="badge badge-info">{}</span>', obj.id_turma.codigo_turma)
        return '-'
    
    @display(description='Status', ordering='status_aluno')
    def status_badge(self, obj):
        colors = {'Activo': 'success', 'Expulso': 'danger', 'Transferido': 'warning'}
        color = colors.get(obj.status_aluno, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status_aluno)
    
    @display(description='Online', boolean=True)
    def online_badge(self, obj):
        return obj.is_online

@admin.register(Encarregado)
class EncarregadoAdmin(ModelAdmin):
    list_display = ['nome_completo', 'email', 'telefone', 'total_educandos']
    search_fields = ['nome_completo', 'email', 'telefone']

    @display(description='Educandos')
    def total_educandos(self, obj):
        count = AlunoEncarregado.objects.filter(id_encarregado=obj).count()
        return format_html('<span class="badge badge-primary">{}</span>', count)

@admin.register(AlunoEncarregado)
class AlunoEncarregadoAdmin(ModelAdmin):
    list_display = ['aluno_nome', 'encarregado_nome', 'grau_parentesco']
    search_fields = ['id_aluno__nome_completo', 'id_encarregado__nome_completo']
    autocomplete_fields = ['id_aluno', 'id_encarregado']

    @display(description='Aluno', ordering='id_aluno__nome_completo')
    def aluno_nome(self, obj):
        return obj.id_aluno.nome_completo

    @display(description='Encarregado', ordering='id_encarregado__nome_completo')
    def encarregado_nome(self, obj):
        return obj.id_encarregado.nome_completo

@admin.register(CargoFuncionario)
class CargoFuncionarioAdmin(ModelAdmin):
    list_display = ['funcionario_nome', 'cargo_nome', 'data_inicio']
    list_filter = ['id_cargo']
    search_fields = ['id_funcionario__nome_completo']
    autocomplete_fields = ['id_funcionario', 'id_cargo']

    @display(description='Funcionário', ordering='id_funcionario__nome_completo')
    def funcionario_nome(self, obj):
         return obj.id_funcionario.nome_completo

    @display(description='Cargo', ordering='id_cargo__nome_cargo')
    def cargo_nome(self, obj):
         return obj.id_cargo.nome_cargo

# =============================================================================
# 3. CURSO, TURMA E MATRIZ
# =============================================================================

@admin.register(Curso)
class CursoAdmin(ModelAdmin):
    list_display = ['nome_curso', 'area_badge', 'duracao', 'total_turmas']
    list_filter = ['id_area_formacao', 'duracao']
    search_fields = ['nome_curso']

    @display(description='Área')
    def area_badge(self, obj):
        if obj.id_area_formacao:
            return format_html('<span class="badge badge-secondary">{}</span>', obj.id_area_formacao.nome_area)
        return '-'
    
    @display(description='Turmas')
    def total_turmas(self, obj):
        count = Turma.objects.filter(id_curso=obj).count()
        return format_html('<span class="badge badge-info">{}</span>', count)

@admin.register(Turma)
class TurmaAdmin(ModelAdmin):
    list_display = ['codigo_turma', 'curso_sigla', 'classe_desc', 'periodo_desc', 'ano', 'total_alunos']
    list_filter = ['id_curso', 'id_classe', 'id_periodo', 'ano']
    search_fields = ['codigo_turma']
    autocomplete_fields = ['id_curso', 'id_sala', 'id_responsavel']
    
    @display(description='Curso')
    def curso_sigla(self, obj):
        return obj.id_curso.nome_curso if obj.id_curso else '-'

    @display(description='Classe')
    def classe_desc(self, obj):
        return f"{obj.id_classe.nivel}ª Classe" if obj.id_classe else '-'

    @display(description='Período')
    def periodo_desc(self, obj):
        return obj.id_periodo.periodo if obj.id_periodo else '-'

    @display(description='Alunos')
    def total_alunos(self, obj):
        count = Aluno.objects.filter(id_turma=obj).count()
        return format_html('<span class="badge badge-success">{}</span>', count)


class MatrizCurricularDisciplinaInline(TabularInline):
    model = MatrizCurricularDisciplina
    extra = 1
    autocomplete_fields = ['id_disciplina']

@admin.register(MatrizCurricular)
class MatrizCurricularAdmin(ModelAdmin):
    list_display = ['descricao', 'curso_no', 'classe_no', 'ano_letivo', 'ativo', 'total_disciplinas']
    list_filter = ['ativo', 'ano_letivo', 'id_curso', 'id_classe']
    inlines = [MatrizCurricularDisciplinaInline]

    @display(description='Curso')
    def curso_no(self, obj):
         return obj.id_curso.nome_curso if obj.id_curso else '-'
    
    @display(description='Classe')
    def classe_no(self, obj):
         return f"{obj.id_classe.nivel}ª" if obj.id_classe else '-'

    @display(description='Qtd. Disciplinas')
    def total_disciplinas(self, obj):
         return obj.disciplinas.count()

# =============================================================================
# 4. DISCIPLINAS E PROFESSORES
# =============================================================================

@admin.register(TipoDisciplina)
class TipoDisciplinaAdmin(ModelAdmin):
    list_display = ['nome_tipo', 'sigla']

@admin.register(Disciplina)
class DisciplinaAdmin(ModelAdmin):
    list_display = ['nome', 'tipo_badge', 'carga_horaria']
    list_filter = ['id_tipo_disciplina']
    search_fields = ['nome']

    @display(description='Tipo')
    def tipo_badge(self, obj):
        if obj.id_tipo_disciplina:
            return format_html('<span class="badge badge-secondary">{}</span>', obj.id_tipo_disciplina.nome_tipo)
        return '-'

@admin.register(ProfessorDisciplina)
class ProfessorDisciplinaAdmin(ModelAdmin):
    list_display = ['professor_nome', 'disciplina_nome', 'turma_codigo']
    list_filter = ['id_disciplina', 'id_turma']
    search_fields = ['id_funcionario__nome_completo', 'id_turma__codigo_turma']
    autocomplete_fields = ['id_funcionario', 'id_disciplina', 'id_turma']

    @display(description='Professor', ordering='id_funcionario__nome_completo')
    def professor_nome(self, obj):
         return obj.id_funcionario.nome_completo

    @display(description='Disciplina', ordering='id_disciplina__nome')
    def disciplina_nome(self, obj):
         return obj.id_disciplina.nome

    @display(description='Turma', ordering='id_turma__codigo_turma')
    def turma_codigo(self, obj):
         return obj.id_turma.codigo_turma

# =============================================================================
# 5. AVALIAÇÕES (NOTAS E FALTAS) - KEY REQUEST
# =============================================================================

@admin.register(Nota)
class NotaAdmin(ModelAdmin):
    """
    Configuração avançada para permitir lançamento de notas em massa.
    Inclui actions personalizadas do Unfold para redirecionar para tela de lançamento.
    """
    
    # Unfold Actions
    @action(description="Lançamento em Massa", icon="playlist_add")
    def lancar_notas_action(self, request):
        return redirect('admin:nota_launch')
    
    lancar_notas_action.attrs = {'class': 'bg-primary-600 text-white hover:bg-primary-700'}
    
    def lancar_notas13_action(self, request):
        return redirect('admin:nota_launch_13')
        
    lancar_notas13_action.short_description = "Notas 13ª Classe"
    lancar_notas13_action.icon = "grade"
    lancar_notas13_action.attrs = {'class': 'bg-indigo-600 text-white hover:bg-indigo-700'}

    # Registrar ações no topo da página (Changelist)
    changelist_actions = ["lancar_notas_action", "lancar_notas13_action"]

    actions_list = [] # Actions na lista (por linha)
    actions_row = [] # Actions na row selection
    actions_detail = [] # Actions no detalhe
    actions_submit_line = [] # Actions no form de submit
    
    # Adicionar botão no topo da lista (changelist)
    # Nota: Unfold usa 'actions_list' ou modificações no template, mas para changelist actions customizadas
    # pode ser necessário usar changelist_actions se suportado ou hackear via override.
    # Unfold suporta `changelist_actions`.
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('lancamento-massivo/', self.admin_site.admin_view(GradeLaunchView.as_view()), name='nota_launch'),
            path('lancamento-13-classe/', self.admin_site.admin_view(GradeLaunch13View.as_view()), name='nota_launch_13'),
        ]
        return custom_urls + urls

    list_display = ['aluno_info', 'disciplina_sigla', 'tipo_avaliacao', 'trimestre', 'valor', 'status_badge']
    list_editable = ['valor'] # Permite editar a nota diretamente na lista!
    list_filter = [
        'trimestre', 
        'tipo_avaliacao', 
        'id_disciplina', 
        'id_aluno__id_turma', # Filtro por Turma do Aluno
        'data_lancamento'
    ]
    search_fields = ['id_aluno__nome_completo', 'id_aluno__numero_matricula']
    list_per_page = 50 # Mostrar mais alunos por página para facilitar lançamento
    autocomplete_fields = ['id_aluno', 'id_disciplina']
    
    @display(description='Aluno', ordering='id_aluno__nome_completo')
    def aluno_info(self, obj):
        return f"{obj.id_aluno.nome_completo} ({obj.id_aluno.id_turma.codigo_turma if obj.id_aluno.id_turma else 'S/T'})"

    @display(description='Disc.', ordering='id_disciplina__nome')
    def disciplina_sigla(self, obj):
        return obj.id_disciplina.nome
    
    @display(description='Status')
    def status_badge(self, obj):
        if obj.valor >= 10:
             return format_html('<span class="badge badge-success">Aprovado</span>')
        return format_html('<span class="badge badge-danger">Reprovado</span>')

@admin.register(FaltaAluno)
class FaltaAlunoAdmin(ModelAdmin):
    list_display = ['aluno_nome', 'disciplina_sigla', 'data_falta', 'justificada']
    list_filter = ['justificada', 'data_falta', 'id_disciplina', 'id_aluno__id_turma']
    search_fields = ['id_aluno__nome_completo']
    autocomplete_fields = ['id_aluno', 'id_disciplina', 'id_turma']

    @display(description='Aluno', ordering='id_aluno__nome_completo')
    def aluno_nome(self, obj):
        return obj.id_aluno.nome_completo

    @display(description='Disciplina', ordering='id_disciplina__sigla')
    def disciplina_sigla(self, obj):
        return obj.id_disciplina.sigla if obj.id_disciplina else '-'

#  =============================================================================
# 6. DOCUMENTOS E SOLICITAÇÕES
# =============================================================================

@admin.register(Documento)
class DocumentoAdmin(ModelAdmin):
    list_display = ['tipo_documento', 'data_emissao', 'ver_arquivo']
    list_filter = ['tipo_documento', 'data_emissao']
    search_fields = ['uuid_documento']

    @display(description='Arquivo')
    def ver_arquivo(self, obj):
        if obj.caminho_pdf:
            return format_html('<a href="{}" target="_blank">Baixar</a>', obj.caminho_pdf.url)
        return '-'

@admin.register(SolicitacaoDocumento)
class SolicitacaoDocumentoAdmin(ModelAdmin):
    list_display = ['id_solicitacao', 'tipo_documento', 'aluno_nome', 'status_badge', 'data_solicitacao']
    list_filter = ['status_solicitacao', 'tipo_documento']
    search_fields = ['id_aluno__nome_completo']
    
    @display(description='Aluno', ordering='id_aluno__nome_completo')
    def aluno_nome(self, obj):
        return obj.id_aluno.nome_completo if obj.id_aluno else '-'

    @display(description='Status')
    def status_badge(self, obj):
        colors = {
            'pendente': 'warning', 
            'pago': 'success', 
            'aguardando_assinatura': 'info', 
            'impresso': 'secondary',
            'disponivel': 'success',
            'rejeitado': 'danger'
        }
        color = colors.get(obj.status_solicitacao, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status_solicitacao.replace('_', ' ').upper())

# =============================================================================
# 7. BIBLIOTECA
# =============================================================================

@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ['nome_categoria']
    search_fields = ['nome_categoria']

@admin.register(Livro)
class LivroAdmin(ModelAdmin):
    list_display = ['titulo', 'categoria_nome']
    list_filter = ['id_categoria']
    search_fields = ['titulo']
    autocomplete_fields = ['id_categoria']

    @display(description='Categoria', ordering='id_categoria__nome_categoria')
    def categoria_nome(self, obj):
        return obj.id_categoria.nome_categoria if obj.id_categoria else '-'

    @display(description='Preço')
    def preco_formatado(self, obj):
        return f"{obj.preco:,.2f} Kz" if obj.preco else 'Grátis'
    
    @display(description='Estoque')
    def estoque_badge(self, obj):
        color = 'success' if obj.quantidade_estoque > 5 else 'danger'
        return format_html('<span class="badge badge-{}">{} un</span>', color, obj.quantidade_estoque)

# =============================================================================
# 8. FINANCEIRO E MATRÍCULAS
# =============================================================================

@admin.register(Fatura)
class FaturaAdmin(ModelAdmin):
    list_display = ['id_fatura', 'aluno_nome', 'descricao', 'total', 'status_badge', 'vencimento']
    list_filter = ['status', 'data_vencimento']
    search_fields = ['id_aluno__nome_completo', 'descricao']
    autocomplete_fields = ['id_aluno']

    @display(description='Aluno')
    def aluno_nome(self, obj):
        return obj.id_aluno.nome_completo if obj.id_aluno else 'N/A'

    @display(description='Status')
    def status_badge(self, obj):
        colors = {'pendente': 'warning', 'paga': 'success', 'vencida': 'danger', 'cancelada': 'dark'}
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status.upper())
    
    @display(description='Vencimento')
    def vencimento(self, obj):
        return obj.data_vencimento

@admin.register(Pagamento)
class PagamentoAdmin(ModelAdmin):
    list_display = ['id_pagamento', 'fatura_info', 'valor_pago', 'metodo_pagamento', 'criado_em']
    list_filter = ['metodo_pagamento']

    @display(description='Fatura')
    def fatura_info(self, obj):
        return f"Ref: {obj.id_fatura.id_fatura} - {obj.id_fatura.descricao}"

    @display(description='Status')
    def status_badge(self, obj):
        colors = {'aprovado': 'success', 'pendente': 'warning', 'rejeitado': 'danger'}
        color = colors.get(obj.status, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.status.upper())

@admin.register(Inscricao)
class InscricaoAdmin(ModelAdmin):
    list_display = ['candidato', 'data_inscricao']
    list_filter = []
    search_fields = ['nome_candidato']

    @display(description='Candidato')
    def candidato(self, obj):
        return obj.nome_candidato

@admin.register(Matricula)
class MatriculaAdmin(ModelAdmin):
    list_display = ['aluno_nome', 'turma_codigo', 'ativo', 'data_matricula']
    list_filter = ['ativo', 'id_turma']
    autocomplete_fields = ['id_aluno', 'id_turma']

    @display(description='Aluno')
    def aluno_nome(self, obj):
        return obj.id_aluno.nome_completo

    @display(description='Turma')
    def turma_codigo(self, obj):
        return obj.id_turma.codigo_turma

# =============================================================================
# 9. SISTEMA (LOGS E CONFIG)
# =============================================================================

@admin.register(Historico)
class HistoricoAdmin(ModelAdmin):
    list_display = ['id_funcionario', 'id_aluno', 'tipo_accao', 'data_hora']
    list_filter = ['tipo_accao', 'data_hora']
    search_fields = []

@admin.register(HistoricoLogin)
class HistoricoLoginAdmin(ModelAdmin):
    list_display = ['usuario_nome', 'ip_usuario', 'dispositivo', 'hora_entrada']
    list_filter = ['hora_entrada']
    search_fields = ['id_funcionario__email', 'id_aluno__nome_completo', 'id_encarregado__nome_completo']

    @display(description='Usuário')
    def usuario_nome(self, obj):
        if obj.id_funcionario: return obj.id_funcionario.email
        if obj.id_aluno: return obj.id_aluno.numero_matricula or obj.id_aluno.nome_completo
        if obj.id_encarregado: return obj.id_encarregado.email
        return 'Desconhecido'

@admin.register(Notificacao)
class NotificacaoAdmin(ModelAdmin):
    list_display = ['titulo', 'tipo_badge', 'alvo', 'lida', 'data_criacao']
    list_filter = ['tipo', 'lida', 'data_criacao']
    
    @display(description='Tipo')
    def tipo_badge(self, obj):
        colors = {'info': 'info', 'success': 'success', 'warning': 'warning', 'error': 'danger'}
        color = colors.get(obj.tipo, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>', color, obj.tipo.upper())

    @display(description='Destinatário')
    def alvo(self, obj):
        if obj.id_funcionario: return f"Func: {obj.id_funcionario.nome_completo}"
        if obj.id_aluno: return f"Aluno: {obj.id_aluno.nome_completo}"
        if obj.id_encarregado: return f"Enc: {obj.id_encarregado.nome_completo}"
        return "Todos"

@admin.register(ConfiguracaoSistema)
class ConfiguracaoSistemaAdmin(ModelAdmin):
    list_display = ['nome_instituicao', 'nif', 'telefone']
    
    def get_fieldsets(self, request, obj=None):
        eh_geral = request.user.is_superuser
        eh_pedagogico = False
        
        try:
            func = Funcionario.objects.get(email=request.user.email)
            cargo_nome = func.id_cargo.nome_cargo.upper()
            if cargo_nome in ['DIRECTOR GERAL', 'DIRETOR GERAL']:
                eh_geral = True
            elif cargo_nome in ['DIRECTOR PEDAGOGICO', 'DIRETOR PEDAGÓGICO', 'DIRECTOR PEDAGOGICOL']:
                eh_pedagogico = True
        except:
            pass
            
        assinaturas_fields = []
        if eh_geral:
            assinaturas_fields.extend(['assinatura_director', 'carimbo_instituicao'])
            
        # O Pedagogico só mexe na dele e no logo. O Director Geral (se tiver esse campo) também pode mexer na dele (geral)
        if eh_pedagogico or eh_geral:
            assinaturas_fields.append('assinatura_director_pedagogico')
            
        fieldsets = [
            ('Dados da Instituição', {
                'fields': ['nome_instituicao', 'nif', 'endereco', 'telefone', 'email_oficial', 'logo']
            }),
        ]
        
        # Só adiciona aba de assinaturas se for Director
        if assinaturas_fields:
            fieldsets.append(('Assinatura e Carimbo Oficiais', {
                'fields': assinaturas_fields
            }))
            
        # Só Director Geral (e Admin) mexe no sistema
        if eh_geral:
            fieldsets.append(('Sistema', {
                'fields': ['backup_automatico', 'frequencia_backup']
            }))
            
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        eh_pedagogico = False
        try:
            func = Funcionario.objects.get(email=request.user.email)
            if func.id_cargo.nome_cargo.upper() in ['DIRECTOR PEDAGOGICO', 'DIRETOR PEDAGÓGICO', 'DIRECTOR PEDAGOGICOL']:
                eh_pedagogico = True
        except:
            pass
            
        # Director Pedagógico só pode alterar Logo e a sua assinatura. Bloqueia os dados textuais da instituição.
        if eh_pedagogico and not request.user.is_superuser:
            return ['nome_instituicao', 'nif', 'endereco', 'telefone', 'email_oficial']
        return []

    def has_add_permission(self, request):
        if ConfiguracaoSistema.objects.exists():
            return False
        return request.user.is_superuser
        
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        try:
            func = Funcionario.objects.get(email=request.user.email)
            cargo = func.id_cargo.nome_cargo.upper()
            if cargo in ['DIRECTOR GERAL', 'DIRETOR GERAL', 'DIRECTOR PEDAGOGICO', 'DIRETOR PEDAGÓGICO', 'DIRECTOR PEDAGOGICOL']:
                return True
        except:
            pass
        return False