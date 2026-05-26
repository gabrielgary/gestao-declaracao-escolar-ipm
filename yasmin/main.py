from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Any
import uvicorn
from dotenv import load_dotenv
import os
from agent import get_yasmin_agent

load_dotenv()

app = FastAPI(title="Yasmin IA - School Assistant")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Erro de validação: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_executor = get_yasmin_agent()

# Memória de conversa por utilizador (em memória RAM, reinicia com o servidor)
# chave: user_id (str), valor: lista de mensagens {role, content}
chat_histories: dict = {}
MAX_HISTORY = 10  # Máximo de pares de mensagens por utilizador


class ChatMessage(BaseModel):
    message: str
    user_id: Optional[Any] = None
    role: Optional[str] = "student"  # student, admin, parent
    user_token: Optional[str] = None


class ClearHistoryRequest(BaseModel):
    user_id: Optional[Any] = None


@app.get("/")
async def root():
    return {"status": "Yasmin Online", "engine": "Gemini", "version": "2.0"}


@app.post("/chat")
async def chat(msg: ChatMessage):
    try:
        user_id = str(msg.user_id) if msg.user_id else "anonymous"

        # Obter histórico do utilizador (ou criar novo)
        history = chat_histories.get(user_id, [])

        # Processar mensagem com histórico
        response = agent_executor.invoke({
            "input": msg.message,
            "role": msg.role,
            "user_token": msg.user_token,
            "chat_history": history
        })

        output = response["output"]

        # Normalizar output para string
        if isinstance(output, list):
            text_parts = []
            for item in output:
                if isinstance(item, dict):
                    text_parts.append(item.get('text', str(item)))
                else:
                    text_parts.append(str(item))
            output_text = ' '.join(text_parts)
        elif isinstance(output, dict):
            output_text = output.get("text", output.get("content", str(output)))
        elif isinstance(output, str):
            output_text = output
        else:
            output_text = str(output)

        output_text = output_text.strip()

        # Actualizar histórico (manter últimos MAX_HISTORY pares)
        history.append({"role": "user", "content": msg.message})
        history.append({"role": "ai", "content": output_text})

        # Trimmar se necessário
        if len(history) > MAX_HISTORY * 2:
            history = history[-(MAX_HISTORY * 2):]

        chat_histories[user_id] = history

        return {
            "response": output_text,
            "chat_history": history
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear-history")
async def clear_history(body: ClearHistoryRequest):
    """Limpa o histórico de conversa de um utilizador"""
    user_id = str(body.user_id) if body.user_id else "anonymous"
    if user_id in chat_histories:
        del chat_histories[user_id]
    return {"status": "Histórico apagado com sucesso"}


@app.get("/health")
async def health():
    """Endpoint de saúde para verificar se a Yasmin está online"""
    return {
        "status": "online",
        "active_sessions": len(chat_histories),
        "engine": "Gemini"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
