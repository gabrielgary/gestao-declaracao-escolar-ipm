
# ... imports
from apis.models import Nota, MatrizCurricularDisciplina

class NotaInline(TabularInline):
    model = Nota
    extra = 0
    tab = True
    fields = ['id_disciplina', 'tipo_nota', 'trimestre', 'valor']
    # autocomplete_fields = ['id_disciplina'] # Disciplina model registration needs search_fields for this to work
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "id_disciplina":
             # Tentar filtrar disciplinas baseado na turma do aluno
             # No Inline, obter o objeto pai (Aluno) é complexo no query set vázio
             # Mas podemos tentar otimizar depois
             pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# In AlunoAdmin, add: 
# inlines = [NotaInline]
