# app/services/rag_service.py
from app.dependencies.qdrant_client import get_qdrant_client
from app.dependencies.gemini_client import GeminiClient
from app.config import settings
from typing import List, Dict, Any

# Esta clase se encarga de consultar la base de datos de KB y devolver los resultados
class RAGService:
    def __init__(self, gemini: GeminiClient = None):
        self.client = get_qdrant_client()
        self.gemini = gemini or GeminiClient()

    async def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        # calcular embedding para la query
        embeddings = await self.gemini.embed_texts([query])
        vector = embeddings[0]

        # query vector en Qdrant
        hits = self.client.search(
            collection_name=settings.COLLECTION_NAME,
            query_vector=vector,
            limit=top_k,
            with_payload=True,
            # si tu cliente qdrant versión usa 'search' distinto, adapta parámetros
        )

        # hits -> normalizar lista de dicts
        results = []
        for h in hits:
            # h: SearchResult
            payload = getattr(h, "payload", None) or h.get("payload", {}) if isinstance(h, dict) else {}
            text = payload.get("text") or payload.get("content") or ""
            results.append({
                "id": getattr(h, "id", None) or h.get("id"),
                "score": getattr(h, "score", None) or h.get("score"),
                "payload": payload,
                "text": text,
            })
        return results
