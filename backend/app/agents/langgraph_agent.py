import asyncio
from typing import List, Dict, Any
import logging

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from app.services.rag_service import RAGService
from app.services.memory_service import MemoryService
from app.dependencies.gemini_client import GeminiClient
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.config import settings

logger = logging.getLogger(__name__)

# definicion del estado del agente para LangGraph
class AgentState(BaseModel):
    session_id: str 
    user_message: str
    memory: List[Dict[str, str]] = Field(default_factory=list)
    retrieved_docs: List[Dict[str, Any]] = Field(default_factory=list)
    prompt: str = ""
    llm_response: str = ""

# deficioon de los nodos del grafo
async def node_load_memory(state: AgentState) -> AgentState:
    memory = MemoryService.get_memory(state.session_id)
    state.memory = memory
    return state

async def node_retrieve(state: AgentState) -> AgentState:
    rag = RAGService()
    docs = await rag.retrieve(state.user_message, top_k=3)
    state.retrieved_docs = docs
    return state

async def node_build_prompt(state: AgentState) -> AgentState:
    # memoria previa
    memory_block = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in state.memory])

    # docs
    ctx_parts = []
    for d in state.retrieved_docs:
        txt = d.get("text") or (d.get("payload") or {}).get("text", "")
        src = d.get("id") or (d.get("payload") or {}).get("filename") or "fuente"
        ctx_parts.append(f"[{src}]\n{txt}")

    kb_context = "\n\n".join(ctx_parts) if ctx_parts else "No hay contexto relevante en KB."

    state.prompt = f"""
{SYSTEM_PROMPT}

CONVERSACIÓN PREVIA:
{memory_block}

CONTEXT (RAG):
{kb_context}

USUARIO:
{state.user_message}

RESPONDER SIGUIENDO ESTAS REGLAS:
- Utiliza el contexto si existe.
- No inventes.
- Si falta información, pide aclaración.
- Responde en español neutro (Colombia).
- Cierra con "Fuentes: [...]" indicando las fuentes usadas.

RESPUESTA:
"""
    return state
async def node_llm(state: AgentState) -> AgentState:
    gem = GeminiClient()
    try:
        response = await asyncio.wait_for(
            gem.generate_text(state.prompt, max_tokens=512, temperature=0.1),
            timeout=20
        )
    except asyncio.TimeoutError:
        response = "Lo siento, tuve un problema con el servidor (timeout)."

    state.llm_response = response

    # guardar memoria
    MemoryService.add_message(state.session_id, "assistant", response)
    return state



# constructor de agente usando los nodos y flujo definidos
class LangGraphAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id

        # construir gráfico
        graph = StateGraph(AgentState)

        # nodes
        graph.add_node("load_memory", node_load_memory)
        graph.add_node("retrieve", node_retrieve)
        graph.add_node("build_prompt", node_build_prompt)
        graph.add_node("llm", node_llm)

        # edges / flujo
        graph.set_entry_point("load_memory")
        graph.add_edge("load_memory", "retrieve")
        graph.add_edge("retrieve", "build_prompt")
        graph.add_edge("build_prompt", "llm")
        graph.add_edge("llm", END)

        # compilar
        self.app = graph.compile()

    async def run(self, message: str) -> str:
        # guardar mensaje usuario
        MemoryService.add_message(self.session_id, "user", message)

        initial_state = AgentState(
            session_id=self.session_id,
            user_message=message,
        )

        result: AgentState = await self.app.invoke(initial_state)

        # anotación de fuentes
        if result.retrieved_docs:
            sources = [
                d.get("id") or (d.get("payload") or {}).get("filename") or "fuente"
                for d in result.retrieved_docs
            ]
            result.llm_response += f"\n\nFuentes: {', '.join(sources)}"

        return result.llm_response