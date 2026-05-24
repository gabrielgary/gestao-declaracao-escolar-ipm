
from django.contrib import admin
from apis.models import MatrizCurricular, MatrizCurricularDisciplina
from unfold.admin import ModelAdmin, TabularInline

class MatrizCurricularDisciplinaInline(TabularInline):
    model = MatrizCurricularDisciplina
    extra = 1
    tab = True
    autocomplete_fields = ['id_disciplina']

@admin.register(MatrizCurricular)
class MatrizCurricularAdmin(ModelAdmin):
    list_display = ['id_curso', 'id_classe', 'ano_letivo', 'ativo', 'total_disciplinas']
    list_filter = ['id_curso', 'id_classe', 'ativo', 'ano_letivo']
    search_fields = ['descricao', 'id_curso__nome_curso']
    inlines = [MatrizCurricularDisciplinaInline]
    
    @display(description='Total Disciplinas')
    def total_disciplinas(self, obj):
        count = obj.disciplinas.count()
        return format_html('<span class="badge badge-info">{}</span>', count)
