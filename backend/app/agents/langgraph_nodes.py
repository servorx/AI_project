# imports de librerias
import asyncio
from typing import List, Dict, Any
from app.dependencies.gemini_client import GeminiClient
from pydantic import BaseModel, Field

# imports de servicios
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService
from app.prompts.system_prompt import SYSTEM_PROMPT


# definicion del estado del agente para LangGraph
class AgentState(BaseModel):
    session_id: str 
    user_message: str
    intent: str = "unknown"
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

RESPUESTA (no dejes esta sección vacía, responde con al menos 2 frases completas):
"""
    return state

# nuevo nodo para la implementacion de fallbacks, garantiza que el agente NUNCA devuelva una respuesta vacía.
async def node_fallback(state: AgentState) -> AgentState:
    response = state.llm_response.strip()

    if not response:
        if state.retrieved_docs:
            response = (
                "Estoy revisando tu consulta con la información disponible, "
                "pero necesito un poco más de detalles para darte una recomendación precisa."
            )
        else:
            response = (
                "No encontré información en la base de conocimientos para tu consulta. "
                "¿Puedes darme más detalles?"
            )

    state.llm_response = response
    return state

async def node_intent_detection(state: AgentState) -> AgentState:
    gem = GeminiClient()

    prompt = f"""
Clasifica el siguiente mensaje de usuario en uno de estos intents:

- ask_product_info  (Información sobre teclados, switches, marcas)
- ask_price         (Precios, costo, rangos, cotizaciones)
- ask_recommendation (¿Cuál recomiendas? ¿Cuál es mejor?)
- greeting          (hola, buenas, qué tal)
- goodbye           (chao, gracias, hasta luego)
- smalltalk         (mensajes no relacionados con teclados)
- unknown           (si no puedes clasificar)

Mensaje del usuario:
"{state.user_message}"

Responde SOLO con un código de intent, sin explicación.
"""

    try:
        result = await asyncio.wait_for(
            gem.generate_text(prompt, max_tokens=10, temperature=0.3),
            timeout=10
        )
    except asyncio.TimeoutError:
        result = "unknown"

    if not result:
        result = "unknown"

    # Normalizar salida
    intent = result.strip().lower()
    allowed = {
        "ask_product_info",
        "ask_price",
        "ask_recommendation",
        "greeting",
        "goodbye",
        "smalltalk",
        "unknown"
    }

    if intent not in allowed:
        intent = "unknown"

    state.intent = intent
    return state

async def node_llm(state: AgentState) -> AgentState:
    print("=== PROMPT ENVIADO AL LLM ===")
    print(state.prompt)
    print("==============================")
    gem = GeminiClient()
    try:
        response = await asyncio.wait_for(
            gem.generate_text(state.prompt, max_tokens=512, temperature=0.3),
            timeout=20
        )
    except asyncio.TimeoutError:
        response = "Lo siento, tuve un problema con el servidor (timeout)."

    # proteger contra None o vacío
    if not response or not response.strip():
        response = ""

    # guardar en el estado
    state.llm_response = response
    # quitar el comendario para debug de langg
    # state.llm_response = f"[DEBUG LANGGRAPH ASDJHLKDSFASJDLFASDJFAJSDL;FJ] {response}"

    # guardar memoria
    MemoryService.add_message(state.session_id, "assistant", response)

    return state  