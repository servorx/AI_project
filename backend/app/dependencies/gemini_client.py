# app/dependencies/gemini_client.py
import os
import httpx
from typing import List, Dict, Any
from app.config import settings

# TODO: revisar si es necesario cambiar esto por otra ruta 
BASE_URL = "https://generativeai.googleapis.com/v1"

class GeminiClient:
    def __init__(self, api_key: str = None, model: str = None, embedding_model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "models/text-bison-001"
        # embedding model name (puede ser opcional)
        self.embedding_model = embedding_model or settings.GEMINI_EMBEDDING_MODEL or "models/embedding-gecko-001"

        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        # Llamada simple para generar texto con el model.
        url = f"{BASE_URL}/{self.model}:generate"
        payload = {
            "prompt": {"text": prompt},
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # el schema puede variar, busca el campo con el texto de salida
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0].get("content", "")
        # variante: text directo
        return data.get("outputText") or data.get("text") or ""

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Produce embeddings para una lista de textos y retorna una lista de vectores (floats).
        url = f"{BASE_URL}/{self.embedding_model}:embed"
        payload = {"instances": [{"content": t} for t in texts]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=self._headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # dependiendo del formato, extraer arrays de embedding
        embeddings = []
        # soporte para varios formatos:
        if "embeddings" in data:
            for item in data["embeddings"]:
                embeddings.append(item["vector"])
            return embeddings
        if "predictions" in data:
            for p in data["predictions"]:
                embeddings.append(p.get("embedding") or p.get("vector") or p.get("values"))
            return embeddings
        # fallback: parse instances -> embedding
        if "instances" in data:
            for inst in data["instances"]:
                emb = inst.get("embedding") or inst.get("vector")
                embeddings.append(emb)
            return embeddings

        raise ValueError("Formato de respuesta de embeddings no reconocido: " + str(data))
