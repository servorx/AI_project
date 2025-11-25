import asyncio
from typing import List
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.rag_service import RAGService
from app.dependencies.gemini_client import GeminiClient

DEFAULT_K = 3

class CommercialAgent:
    def __init__(self, gemini_client: GeminiClient = None, rag: RAGService = None):
        self.gemini = gemini_client or GeminiClient()
        self.rag = rag or RAGService(self.gemini)

    async def _build_prompt(self, user_message: str, retrieved_docs: List[dict]) -> str:
        # unir contexto
        ctx_parts = []
        for i, doc in enumerate(retrieved_docs, start=1):
            txt = doc.get("text") or doc.get("payload", {}).get("text", "")
            score = doc.get("score")
            ctx_parts.append(f"[DOC {i} | score={score}]\n{txt}\n")

        kb_context = "\n".join(ctx_parts) if ctx_parts else "No hay contexto relevante en KB."

        prompt = f"""
{SYSTEM_PROMPT}

CONTEXT (del KB, usa SOLO si es relevante):
{kb_context}

INSTRUCCIONES:
- Responde en español neutro (Colombia).
- Sé claro y conciso, orientado a ayudar y vender sin presionar.
- Siempre prioriza la información del CONTEXT si está disponible.
- Si la KB no contiene la respuesta o hay ambigüedad, pide más datos al usuario (p.ej.: modelo buscado, presupuesto, uso).
- No inventes datos ni precios. Si no sabes, dilo claramente y ofrece pedir más información.

USUARIO:
{user_message}

RESPUESTA:
"""
        return prompt

    async def run(self, message: str, top_k: int = DEFAULT_K) -> str:
        # Recuperar contexto (RAG)
        docs = await self.rag.retrieve(message, top_k=top_k)

        # Construir prompt
        prompt = await self._build_prompt(message, docs)

        # Llamar a Gemini para generar respuesta
        # usa temperatura baja para respuestas concretas
        response = await self.gemini.generate_text(prompt, max_tokens=512, temperature=0.0)
        # opcional: post-process (trim, seguridad)
        return response.strip()
