from typing import List, Dict, Any
from app.dependencies.qdrant_client import get_qdrant_client
from app.dependencies.gemini_client import GeminiClient
from app.config import settings

# Esta clase se encarga de consultar la base de datos de KB y devolver los resultados
class RAGService:
    def __init__(self, gemini: GeminiClient = None):
        self.client = get_qdrant_client()
        self.gemini = gemini or GeminiClient()

    async def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        # busqueda estandar de qdrant para responder mensajes con RAG a traves del embedding
        embeddings = await self.gemini.embed_texts([query])
        vector = embeddings[0]

        # nuevo método de qdrant para búsquedas vectoriales
        hits = self.client.query_points(
            collection_name=settings.QDRANT_COLLECTION,
            query=vector,
            limit=top_k,
            with_payload=True
        )
        print(f"[RAG] VECTOR length={len(vector)}")
        print(f"[RAG] HITS raw response: {hits}")
        results = []
        for h in hits.points:
            payload = h.payload or {}
            results.append({
                "id": h.id,
                "score": h.score,
                "payload": payload,
                "text": payload.get("text") or payload.get("content") or "",
            })
        return results

    # Extraccion de preferencias del usuario 
    async def extract_preferences(self, limit: int = 5) -> Dict[str, Any]:
        # Extraer preferencias desde la KB y las transforma en un JSON estructurado
        # 1. Obtener últimos items de la KB (scroll)
        scroll_result = self.client.scroll(
            collection_name=settings.QDRANT_COLLECTION,
            limit=limit,
            scroll_filter=None,
            with_payload=True
        )

        points, _ = scroll_result  # (points, next_page_offset)

        if not points:
            return {}

        # 2. Unir texto relevante
        history_text = "\n".join([
            p.payload.get("text") or p.payload.get("content") or ""
            for p in points
        ])

        if not history_text.strip():
            return {}

        # 3. Prompt para estructurar preferencias reales
        prompt = f"""
        Analiza el siguiente historial del cliente y detecta sus preferencias REALES 
        sobre teclados mecánicos, solo si están explícitas.

        Extrae únicamente:
        - tipo de teclado (ej: mecánico, low profile,…)
        - formato (full, TKL, 75%, 65%, 60%)
        - switch preferido (red, brown, blue, silent,…)
        - presupuesto máximo
        - prioridades (ergonomía, tamaño, precio, ruido)

        Responde únicamente un JSON válido. No inventes datos si no están.
        
        Historial:
        {history_text}
        """

        # 4. Llamar a Gemini
        response_text = await self.gemini.generate_text(prompt, max_tokens=300)

        # Intentar parsear JSON suavemente
        import json
        try:
            return json.loads(response_text)
        except:
            # Si falla, devolver como texto
            return {"raw_response": response_text}
