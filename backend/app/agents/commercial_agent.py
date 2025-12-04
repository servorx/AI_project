import asyncio
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.rag_service import RAGService
from app.dependencies.gemini_client import GeminiClient
from app.services.memory_service import MemoryService

class CommercialAgent:
    def __init__(self, session_id: str, gemini_client: GeminiClient = None, rag: RAGService = None):
        self.session_id = session_id
        self.gemini = gemini_client or GeminiClient()
        self.rag = rag or RAGService(self.gemini)

    async def _build_prompt(self, user_message: str, retrieved_docs):

        # 1. recuperar memoria
        memory = MemoryService.get_memory(self.session_id)
        memory_block = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in memory])

        # 2. contexto por RAG
        ctx_parts = []
        for d in retrieved_docs:
            ctx_parts.append(d.get("text") or d["payload"].get("text", ""))

        kb_context = "\n---\n".join(ctx_parts) if ctx_parts else "No hay contexto relevante en KB."

        # 3. construir prompt completo
        prompt = f"""
{SYSTEM_PROMPT}

CONVERSACIÓN PREVIA:
{memory_block}

CONTEXT (RAG):
{kb_context}

USER:
{user_message}

ASSISTANT:
"""

        return prompt

    async def run(self, message: str):
        # guardar mensaje del usuario en memoria
        MemoryService.add_message(self.session_id, "user", message)

        # recuperar contexto
        docs = await self.rag.retrieve(message)

        # construir prompt
        prompt = await self._build_prompt(message, docs)

        # LLM
        response = await self.gemini.generate_text(prompt)

        # guardar respuesta en memoria
        MemoryService.add_message(self.session_id, "assistant", response)

        return response
