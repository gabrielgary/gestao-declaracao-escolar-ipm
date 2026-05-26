from langchain.tools import tool
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from contextvars import ContextVar

load_dotenv()

DJANGO_API_URL = os.getenv("DJANGO_BACKEND_URL", "http://localhost:8000")

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
def gerar_backup(nome_personalizado: str = "") -> str:
    """
    Gera um novo backup da base de dados do sistema e permite renomeá-lo.
    Usa o nome_personalizado fornecido pelo utilizador para nomear o ficheiro.
    Se nome_personalizado estiver vazio, usa o timestamp automático.
    Apenas para Administradores/Funcionários.
    """
    try:
        headers = get_headers()
        headers["Content-Type"] = "application/json"

        # 1. Disparar o backup no Django
        url = f"{DJANGO_API_URL}/api/v1/backups/run_backup/"
        response = requests.post(url, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            data = response.json()
            filename_original = data.get('filename', '')

            # 2. Se nome personalizado foi fornecido, renomear o ficheiro
            if nome_personalizado.strip() and filename_original:
                novo_nome = _renomear_backup(filename_original, nome_personalizado.strip(), headers)
                if novo_nome:
                    return (
                        f"✅ Backup gerado e renomeado com sucesso!\n"
                        f"- Nome original: {filename_original}\n"
                        f"- Novo nome: {novo_nome}\n"
                        f"- Criado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
                    )

            return (
                f"✅ Backup gerado com sucesso!\n"
                f"- Ficheiro: {filename_original}\n"
                f"- Criado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
            )
        elif response.status_code == 401:
            return "Erro de autorização. Por favor, faça login novamente."
        elif response.status_code == 403:
            return "Apenas administradores podem gerar backups."
        else:
            return f"Erro ao gerar backup (Status: {response.status_code}): {response.text}"

    except requests.exceptions.Timeout:
        return "O processo de backup demorou demasiado. O sistema pode estar ocupado. Tente novamente."
    except requests.exceptions.ConnectionError:
        return "Não consigo conectar ao servidor. Verifique se o backend está ativo."
    except Exception as e:
        return f"Erro inesperado ao gerar backup: {str(e)}"


def _renomear_backup(nome_original: str, novo_nome: str, headers: dict) -> str:
    """
    Renomeia um ficheiro de backup no servidor.
    Estratégia: descarrega a lista de backups, encontra o ficheiro e renomeia localmente via os.rename.
    Como a API Django não tem endpoint de rename, fazemos via manipulação directa do ficheiro.
    Retorna o novo nome ou None se falhar.
    """
    try:
        import re
        # Garantir que o novo nome tem extensão .sql
        nome_limpo = re.sub(r'[^\w\-_\.]', '_', novo_nome)
        if not nome_limpo.endswith('.sql'):
            nome_limpo = f"{nome_limpo}.sql"

        # Caminho directo ao ficheiro (assumindo estrutura padrão do WAMP)
        media_root = os.getenv("DJANGO_MEDIA_ROOT", "")
        if media_root:
            caminho_original = os.path.join(media_root, 'backups', nome_original)
            caminho_novo = os.path.join(media_root, 'backups', nome_limpo)
            if os.path.exists(caminho_original):
                os.rename(caminho_original, caminho_novo)
                return nome_limpo

        return None
    except Exception:
        return None


@tool
def listar_backups() -> str:
    """
    Lista todos os backups disponíveis no sistema com nome, tamanho e data de criação.
    Apenas para Administradores/Funcionários.
    """
    try:
        headers = get_headers()
        url = f"{DJANGO_API_URL}/api/v1/backups/"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            backups = response.json()
            if not backups:
                return "Nenhum backup encontrado no sistema."

            linhas = ["💾 Backups disponíveis:\n"]
            for i, b in enumerate(backups[:10], 1):
                tamanho_kb = round(b.get('size', 0) / 1024, 1)
                data_raw = b.get('created_at', '')
                try:
                    dt = datetime.fromisoformat(data_raw)
                    data_fmt = dt.strftime('%d/%m/%Y às %H:%M')
                except Exception:
                    data_fmt = data_raw

                linhas.append(f"{i}. 📁 {b.get('filename', 'N/A')}")
                linhas.append(f"   Tamanho: {tamanho_kb} KB | Data: {data_fmt}")

            return '\n'.join(linhas)
        elif response.status_code == 401:
            return "Erro de autorização. Por favor, faça login novamente."
        elif response.status_code == 403:
            return "Apenas administradores podem listar backups."
        return f"Erro ao listar backups (Status: {response.status_code})"

    except requests.exceptions.Timeout:
        return "O sistema não está respondendo. Tente novamente mais tarde."
    except requests.exceptions.ConnectionError:
        return "Não consigo conectar ao servidor. Verifique se o backend está ativo."
    except Exception as e:
        return f"Erro ao listar backups: {str(e)}"
