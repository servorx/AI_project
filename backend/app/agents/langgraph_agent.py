import asyncio
from typing import List, Dict, Any
import logging
from enum import Enum

from backend.app.agents.langgraph_nodes import node_load_memory, node_retrieve, node_build_prompt, node_llm, node_fallback, AgentState
from langgraph.graph import StateGraph, END

from app.services.rag_service import RAGService
from backend.app.services.memory_service import MemoryService
from app.dependencies.gemini_client import GeminiClient
from app.config import settings

# obtiene el loger con el nombre en especifico
logger = logging.getLogger(__name__)

# define un enum para los intent de los agentes
class Intent(str, Enum):
    ASK_PRODUCT_INFO = "ask_product_info"
    ASK_PRICE = "ask_price"
    ASK_RECOMMENDATION = "ask_recommendation"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    SMALLTALK = "smalltalk"
    UNKNOWN = "unknown"

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
        graph.add_node("fallback", node_fallback)

        # edges / flujo
        graph.set_entry_point("load_memory")
        graph.add_edge("load_memory", "retrieve")
        graph.add_edge("retrieve", "build_prompt")
        graph.add_edge("build_prompt", "llm")
        graph.add_edge("llm", "fallback")
        graph.add_edge("fallback", END)

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

