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

    # se puede implementar en el prompt de langgraph 
    # - Cierra con "Fuentes: [...]" indicando las fuentes usadas.
    # pero solo para modo de desarrollo porque esto en realidad no es necesario
    source_option = "Fuentes: [...]" if settings.SHOW_SOURCES else ""
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
{source_option}

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
    # quitar el comendario para debug de langgraph 
    # state.llm_response = "[LANGGRAPH OKADFKLN;SDHJVDFSDFLJKVSNFDLKVNSDJFLKVSNDFLVSNDFJLVSDNFKV] " + response

    # guardar memoria
    MemoryService.add_message(state.session_id, "assistant", response)
    return state

# constructor de agente usando los nodos y flujo definidos
class LangGraphAgent:
    def __init__(self, session_id: str, gemini_client: GeminiClient = None, rag: RAGService = None):
        self.session_id = session_id
        self.gemini = gemini_client or GeminiClient()
        self.rag = rag or RAGService(self.gemini)

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

        # usar ainvoke (async)
        res = await self.app.ainvoke(initial_state)

        # res puede ser dict o AgentState
        if isinstance(res, dict):
            retrieved_docs = res.get("retrieved_docs") or []
            llm_response = res.get("llm_response") or res.get("llm") or ""
        else:
            # pydantic model
            retrieved_docs = getattr(res, "retrieved_docs", []) or []
            llm_response = getattr(res, "llm_response", "") or getattr(res, "llm", "")

        # seguridad adicional: normalizar docs a lista de dict
        if retrieved_docs is None:
            retrieved_docs = []

        # construir fuentes si existen
        sources = []
        for d in retrieved_docs:
            if isinstance(d, dict):
                src = d.get("id") or (d.get("payload") or {}).get("filename") or ""
            else:
                # si d es objeto con .payload .id
                src = getattr(d, "id", None) or (getattr(d, "payload", {}) or {}).get("filename") or ""
            if src:
                sources.append(str(src))

        # mostrar o no las fuentes según config
        if settings.SHOW_SOURCES:
            # mostrar fuentes si hay alguna
            if sources:
                llm_response = f"{llm_response}\n\nFuentes: {', '.join(sources)}"
            # no mostrar fuentes si no hay
            else:
                llm_response = f"{llm_response}\n\nFuentes: Ninguna"
        else:
            # NO mostrar fuentes en modo producción o cuando esté desactivado
            pass

        # guardar en memoria (opcional)
        MemoryService.add_message(self.session_id, "assistant", llm_response)

        return llm_response

