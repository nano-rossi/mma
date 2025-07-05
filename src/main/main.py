import os
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOpenAI as CommunityChatOpenAI
import asyncio
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
# Configuración de OpenAI y Telegram
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL_OPEN_AI = os.environ.get("MODEL_OPEN_AI", "gpt-4o-mini")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

class QueryRequest(BaseModel):
    query: str
    chat_id: int

# Configurar la conexión a SQLite para LangChain
sqlite_uri = "sqlite:///chinook.db"
db = SQLDatabase.from_uri(sqlite_uri)

llm = CommunityChatOpenAI(
    temperature=0,
    model=MODEL_OPEN_AI,
    api_key=OPENAI_API_KEY,
    max_retries=2,
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    handle_parsing_errors=True,
    max_iterations=5,
    max_execution_time=30,
)

async def procesar_y_responder(request: QueryRequest):
    try:
        result = await agent.ainvoke({
            "input": (
                f"Eres un asistente de Business Intelligence, tu objetivo es responder preguntas sobre la base de datos de la empresa. "
                f"Tienes a disposición la conexión a SQLite para revisar los datos. "
                f"Si la consulta no está relacionada a datos de la empresa, responde: "
                f"Lo siento, no te puedo ayudar con eso. "
                f"La consulta es la siguiente: {request.query}"
            )
        })
        answer = result['output'] if isinstance(result, dict) and 'output' in result else str(result)
    except Exception as e:
        answer = f"Error al procesar la consulta: {str(e)}"

    payload = {
        "chat_id": request.chat_id,
        "text": answer
    }

    try:
        resp = requests.post(TELEGRAM_API_URL, json=payload)
        resp.raise_for_status()
    except Exception as e:
        return {"ok": False, "error": str(e), "answer": answer}
    return {"ok": True, "answer": answer} 


@app.post("/query")
async def query_endpoint(request: QueryRequest):
    # Responder rápido al cliente
    asyncio.create_task(procesar_y_responder(request))
    return {"ok": True}