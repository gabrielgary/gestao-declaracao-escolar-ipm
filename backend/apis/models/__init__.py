# Importar todos os models para facilitar o uso

from .base import BaseModel

from .usuarios import Cargo, Funcionario, Encarregado, CargoFuncionario

from .alunos import Aluno, AlunoEncarregado

from .academico import (

    Sala, Classe, Departamento, Seccao, AreaFormacao,

    Curso, Periodo, Turma, Horario, MatrizCurricular, MatrizCurricularDisciplina

)

from .avaliacoes import TipoDisciplina, Disciplina, ProfessorDisciplina, Nota, FaltaAluno

from .documentos import Documento, SolicitacaoDocumento, HistoricoTurmaAluno

from .biblioteca import Categoria, Livro

from .financeiro import Fatura, Pagamento

from .matriculas import Inscricao, Matricula

from .auditoria import Historico, HistoricoLogin, Notificacao,ConfiguracaoSistema

 

__all__ = [

    'BaseModel',

    'Cargo', 'Funcionario', 'Encarregado', 'CargoFuncionario',

    'Aluno', 'AlunoEncarregado',

    'Sala', 'Classe', 'Departamento', 'Seccao', 'AreaFormacao', 'Curso', 'Periodo', 'Turma', 'Horario',

    'MatrizCurricular', 'MatrizCurricularDisciplina',

    'TipoDisciplina', 'Disciplina',  'ProfessorDisciplina', 'Nota', 'FaltaAluno',

    'Documento', 'SolicitacaoDocumento', 'HistoricoTurmaAluno',

    'Categoria', 'Livro',

    'Fatura', 'Pagamento',

    'Inscricao', 'Matricula',

    'Historico', 'HistoricoLogin','Notificacao','ConfiguracaoSistema'

]

