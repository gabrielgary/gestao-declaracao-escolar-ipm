from langchain.tools import tool
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from contextvars import ContextVar

load_dotenv()

DJANGO_API_URL = os.getenv("DJANGO_BACKEND_URL", "http://localhost:8000")

# Importar o contexto do token do usuário
try:
    from agent import user_token_context
except ImportError:
    user_token_context: ContextVar[str] = ContextVar('user_token', default=None)


def get_headers():
    token = user_token_context.get()
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@tool
def verify_student(query: str) -> str:
    """
    Pesquisa um aluno no sistema usando nome, matrícula ou BI.
    Retorna os detalhes do aluno se encontrado.
    """
    try:
        headers = get_headers()
        url = f"{DJANGO_API_URL}/api/v1/alunos/?search={query}"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data['count'] > 0:
                aluno = data['results'][0]
                return (
                    f"Aluno encontrado:\n"
                    f"- Nome: {aluno['nome_completo']}\n"
                    f"- Matrícula: {aluno.get('numero_matricula', 'N/A')}\n"
                    f"- Curso: {aluno.get('id_turma_codigo', 'N/A')}\n"
                    f"- Status: {aluno['status_aluno']}"
                )
            return "Nenhum aluno encontrado com esses dados."
        elif response.status_code == 401:
            return "Erro de autorização. Por favor, faça login novamente no sistema."
        elif response.status_code == 403:
            return "Você não tem permissão para aceder a essa informação."
        return f"Erro na comunicação com o sistema (Status: {response.status_code})"
    except requests.exceptions.Timeout:
        return "O sistema de gestão escolar não está respondendo. Tente novamente mais tarde."
    except requests.exceptions.ConnectionError:
        return "Não consigo conectar ao sistema de gestão escolar. Verifique se o servidor backend está ativo."
    except Exception:
        return "Erro ao verificar aluno. Por favor, contacte o suporte técnico."


@tool
def get_academic_stats() -> str:
    """
    Retorna estatísticas gerais do sistema (apenas para Administradores/Funcionários).
    Inclui total de alunos, solicitações pendentes e receita total.
    """
    try:
        headers = get_headers()
        url = f"{DJANGO_API_URL}/api/v1/dashboard/stats/"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            kpis = data.get('kpis', {})
            total_alunos = kpis.get('novos_alunos', {}).get('total', 0)
            total_solicitacoes = kpis.get('total_solicitacoes', {}).get('total', 0)
            receita = kpis.get('receita_total', {}).get('total', 0)
            return (
                f"📊 Estatísticas Gerais do Sistema:\n"
                f"- Total de Alunos: {total_alunos}\n"
                f"- Total de Solicitações: {total_solicitacoes}\n"
                f"- Receita Total: {receita} Kz"
            )
        elif response.status_code == 401:
            return "Erro de autorização. Por favor, faça login novamente."
        elif response.status_code == 403:
            return "Apenas administradores podem ver essas estatísticas."
        return f"Erro ao obter estatísticas (Status: {response.status_code})"
    except requests.exceptions.Timeout:
        return "O sistema não está respondendo. Tente novamente mais tarde."
    except requests.exceptions.ConnectionError:
        return "Não consigo conectar ao sistema de gestão. Verifique se o servidor está ativo."
    except Exception:
        return "Erro ao obter estatísticas. Por favor, contacte o suporte técnico."


@tool
def get_solicitacoes_resumo() -> str:
    """
    Retorna um resumo detalhado das solicitações de documentos:
    contagem por status (pendente, pago, processando, disponivel, rejeitado)
    e as 5 mais recentes. Apenas para Administradores/Funcionários.
    """
    try:
        headers = get_headers()
        url = f"{DJANGO_API_URL}/api/v1/solicitacoes/?page_size=100"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            resultados = data.get('results', [])
            total = data.get('count', len(resultados))

            # Agrupar por status
            status_map = {
                'pendente': 0,
                'pago': 0,
                'processando': 0,
                'disponivel': 0,
                'rejeitado': 0
            }
            tipo_map = {}

            for s in resultados:
                st = s.get('status_solicitacao', 'pendente')
                if st in status_map:
                    status_map[st] += 1
                tipo = s.get('tipo_documento', 'Outro')
                tipo_map[tipo] = tipo_map.get(tipo, 0) + 1

            # Top tipos de documento
            top_tipos = sorted(tipo_map.items(), key=lambda x: x[1], reverse=True)[:3]
            top_tipos_str = ', '.join([f"{t[0]} ({t[1]})" for t in top_tipos])

            # Últimas 5
            recentes = resultados[:5]
            recentes_str = '\n'.join([
                f"  • {r.get('tipo_documento', 'N/A')} — {r.get('aluno_nome', 'N/A')} [{r.get('status_solicitacao', 'N/A')}]"
                for r in recentes
            ])

            return (
                f"📋 Resumo de Solicitações de Documentos:\n\n"
                f"Total: {total} solicitações\n\n"
                f"Por status:\n"
                f"- ⏳ Pendente: {status_map['pendente']}\n"
                f"- 💰 Pago: {status_map['pago']}\n"
                f"- ⚙️ Processando: {status_map['processando']}\n"
                f"- ✅ Disponível: {status_map['disponivel']}\n"
                f"- ❌ Rejeitado: {status_map['rejeitado']}\n\n"
                f"Documentos mais solicitados: {top_tipos_str}\n\n"
                f"Mais recentes:\n{recentes_str}"
            )
        elif response.status_code == 401:
            return "Erro de autorização. Por favor, faça login novamente."
        elif response.status_code == 403:
            return "Apenas funcionários podem ver o resumo de solicitações."
        return f"Erro ao obter solicitações (Status: {response.status_code})"
    except requests.exceptions.Timeout:
        return "O sistema não está respondendo. Tente novamente mais tarde."
    except requests.exceptions.ConnectionError:
        return "Não consigo conectar ao servidor. Verifique se o backend está ativo."
    except Exception as e:
        return f"Erro ao obter resumo de solicitações: {str(e)}"


@tool
def get_documentos_gerados() -> str:
    """
    Retorna estatísticas dos documentos já gerados (status 'disponivel'):
    quantos PDFs foram gerados por tipo e data do mais recente.
    Apenas para Administradores/Funcionários.
    """
    try:
        headers = get_headers()
        url = f"{DJANGO_API_URL}/api/v1/solicitacoes/?page_size=200"
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            todos = data.get('results', [])

            # Filtrar apenas disponíveis (documentos gerados)
            gerados = [s for s in todos if s.get('status_solicitacao') == 'disponivel']
            total_gerados = len(gerados)

            if total_gerados == 0:
                return "Nenhum documento foi gerado ainda."

            # Agrupar por tipo
            tipo_map = {}
            for s in gerados:
                tipo = s.get('tipo_documento', 'Outro')
                tipo_map[tipo] = tipo_map.get(tipo, 0) + 1

            tipos_str = '\n'.join([f"  • {t}: {c}" for t, c in sorted(tipo_map.items(), key=lambda x: x[1], reverse=True)])

            # Data do mais recente
            datas = [s.get('data_solicitacao') for s in gerados if s.get('data_solicitacao')]
            mais_recente = max(datas) if datas else 'N/A'
            if mais_recente != 'N/A':
                try:
                    dt = datetime.fromisoformat(mais_recente.replace('Z', '+00:00'))
                    mais_recente = dt.strftime('%d/%m/%Y às %H:%M')
                except Exception:
                    pass

            return (
                f"📄 Documentos Gerados (PDF disponíveis):\n\n"
                f"Total gerado: {total_gerados} documentos\n\n"
                f"Por tipo:\n{tipos_str}\n\n"
                f"Mais recente gerado em: {mais_recente}"
            )
        elif response.status_code == 401:
            return "Erro de autorização. Por favor, faça login novamente."
        elif response.status_code == 403:
            return "Apenas funcionários podem ver os documentos gerados."
        return f"Erro ao obter documentos (Status: {response.status_code})"
    except requests.exceptions.Timeout:
        return "O sistema não está respondendo. Tente novamente mais tarde."
    except requests.exceptions.ConnectionError:
        return "Não consigo conectar ao servidor. Verifique se o backend está ativo."
    except Exception as e:
        return f"Erro ao obter documentos gerados: {str(e)}"
