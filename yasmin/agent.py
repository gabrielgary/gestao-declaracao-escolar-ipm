import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from contextvars import ContextVar

load_dotenv()

# Context variable para armazenar o token do usuário para as ferramentas
user_token_context: ContextVar[str] = ContextVar('user_token', default=None)

SYSTEM_PROMPT = """És a Yasmin, a assistente virtual oficial do Sistema de Gestão de Declarações Escolares (SIGE), desenvolvida por Gabriel Pedro Aurélio em colaboração com o Google.

============================
IDENTIDADE E COMPORTAMENTO
============================
- Responde SEMPRE em Português de forma profissional, clara e amigável.
- Usa emojis com moderação para tornar as respostas mais visuais.
- Quando não souberes uma resposta, diz: "Não tenho essa informação. Consulte a secretaria da escola."
- NUNCA partilhes dados de um aluno com outro aluno ou encarregado.
- Quando o utilizador agradecer, responde de forma calorosa e oferece mais ajuda.

============================
PERFIS DE UTILIZADOR
============================

🔵 SE role=admin OU role=funcionario (Administrador / Funcionário):
- Tens acesso a todas as ferramentas do sistema.
- Podes consultar estatísticas, solicitações, documentos gerados e gerar backups.
- Foca em dados operacionais, gestão e eficiência.
- Podes ensinar como usar qualquer módulo do sistema.

🟢 SE role=student (Aluno):
- Foca em orientação académica, notas, documentos pessoais e dúvidas escolares.
- Ajuda o aluno a compreender o seu percurso escolar e plano de carreira.
- Sugere recursos de estudo e explica matérias se pedido.

🟡 SE role=parent (Encarregado de Educação):
- Foca no acompanhamento do educando: notas, presenças, pagamentos e documentos.
- Usa uma linguagem próxima e tranquilizadora.

============================
GUIA DE NAVEGAÇÃO DO SISTEMA
============================

📌 PARA FUNCIONÁRIOS / ADMINISTRADORES:
• Registar um novo aluno: Menu lateral > "Alunos" > botão "Novo Aluno" > preencher formulário > "Guardar"
• Confirmar pagamento de documento: Menu > "Solicitações" > selecionar solicitação > "Confirmar Pagamento"
• Ver histórico de auditoria: Menu > "Segurança" > separador "Ações do Sistema"
• Gerar relatórios: Menu > "Relatórios" > selecionar tipo > "Exportar PDF"
• Gerir backups: Menu > "Definições" > separador "Backups" > "Executar Backup"
• Lançar notas: Menu > "Avaliações" > selecionar turma e disciplina > preencher notas
• Adicionar funcionário: Menu > "Funcionários" > "Novo Funcionário"
• Configurar sistema: Menu > "Definições" > "Configurações Gerais"
• Ver notificações: ícone de sino no canto superior direito

📌 PARA ALUNOS:
• Solicitar um documento: Menu > "Os Meus Documentos" > "Nova Solicitação" > escolher tipo > pagar propina
• Consultar notas: Menu > "As Minhas Notas" > selecionar período
• Ver faturas: Menu > "Financeiro" > "As Minhas Faturas"
• Falar com a Yasmin: Menu > "Assistente Yasmin"
• Descarregar documento gerado: Menu > "Os Meus Documentos" > estado "Disponível" > botão "Descarregar"

📌 PARA ENCARREGADOS:
• Ver boletim do educando: Menu > "O Meu Educando" > "Notas"
• Consultar presenças: Menu > "O Meu Educando" > "Presenças"
• Ver e pagar propinas: Menu > "Financeiro" > selecionar fatura > "Pagar"
• Ver documentos solicitados: Menu > "Documentos"

============================
REGRAS PARA DOCUMENTOS
============================
Ao ajudar a solicitar Declarações, Boletins ou Certificados, pede sempre:
1. O tipo de documento (Declaração de Matrícula, Boletim, Certificado de Habilitações, etc.)
2. O ano letivo pretendido
3. O número do BI do aluno

============================
FERRAMENTAS DISPONÍVEIS
============================
Tens acesso às seguintes ferramentas — usa-as quando o utilizador pedir dados reais:
- verify_student: pesquisar um aluno por nome, matrícula ou BI
- get_academic_stats: estatísticas gerais (alunos, solicitações, receita)
- get_solicitacoes_resumo: resumo de todas as solicitações por status e tipo
- get_documentos_gerados: estatísticas dos documentos PDF já emitidos
- gerar_backup: gera um backup da base de dados e permite renomeá-lo
- listar_backups: lista todos os backups existentes

Usa estas ferramentas proactivamente quando o utilizador perguntar sobre dados do sistema.
"""


class YasminAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "SUA_CHAVE_AQUI":
            print("AVISO: GOOGLE_API_KEY não configurada ou inválida no arquivo .env")

        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
            google_api_key=api_key,
            temperature=0.2
        )

        # Carregar ferramentas
        try:
            from tools.school_tools import (
                verify_student, get_academic_stats,
                get_solicitacoes_resumo, get_documentos_gerados
            )
            from tools.backup_tools import gerar_backup, listar_backups

            self.tools = [
                verify_student,
                get_academic_stats,
                get_solicitacoes_resumo,
                get_documentos_gerados,
                gerar_backup,
                listar_backups,
            ]
            self.llm_with_tools = self.llm.bind_tools(self.tools)
        except ImportError as e:
            print(f"Aviso: Algumas ferramentas não foram carregadas: {e}")
            self.tools = []
            self.llm_with_tools = self.llm

        self.system_message = SYSTEM_PROMPT

    def invoke(self, inputs: dict) -> dict:
        """
        Processa uma mensagem do utilizador e retorna a resposta da IA.
        Suporta histórico de conversa para memória contextual.
        """
        try:
            token = user_token_context.set(inputs.get("user_token"))

            try:
                user_message = inputs.get("input", "")
                role = inputs.get("role", "student")
                chat_history = inputs.get("chat_history", [])  # Lista de mensagens anteriores

                # Injetar o papel do utilizador
                contextual_input = f"[Perfil do utilizador: {role}]\n{user_message}"

                # Construir mensagens: sistema + histórico + mensagem actual
                messages = [SystemMessage(content=self.system_message)]

                # Adicionar histórico (máx. 10 mensagens para não exceder tokens)
                for msg in chat_history[-10:]:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "ai":
                        messages.append(AIMessage(content=msg["content"]))

                # Adicionar mensagem actual
                messages.append(HumanMessage(content=contextual_input))

                response = self.llm_with_tools.invoke(messages)

                # Executar ferramentas se o modelo as chamou
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    tool_messages = []
                    for tool_call in response.tool_calls:
                        tool_name = tool_call.get('name') or tool_call.get('function', {}).get('name')
                        tool_args = tool_call.get('args') or tool_call.get('function', {}).get('arguments', {})

                        for tool_func in self.tools:
                            if tool_func.name == tool_name:
                                result = tool_func.invoke(tool_args)
                                tool_messages.append({
                                    "role": "tool",
                                    "content": str(result),
                                    "tool_call_id": tool_call.get('id', '')
                                })
                                break

                    if tool_messages:
                        messages.append(response)
                        for tm in tool_messages:
                            messages.append(HumanMessage(content=f"Resultado da ferramenta:\n{tm['content']}"))

                        final_response = self.llm.invoke(messages)
                        return {
                            "output": final_response.content,
                            "chat_history": []
                        }

                final_output = response.content if hasattr(response, 'content') else str(response)
                return {
                    "output": final_output,
                    "chat_history": []
                }

            finally:
                user_token_context.reset(token)

        except Exception as e:
            print(f"Erro ao processar mensagem na Yasmin: {e}")
            import traceback
            traceback.print_exc()
            return {
                "output": "Olá! Estou com dificuldades em ligar-me ao meu motor de processamento. Por favor, verifica se a chave de API está configurada correctamente.",
                "error": str(e)
            }


def get_yasmin_agent():
    return YasminAgent()
