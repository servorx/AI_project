import asyncio
import httpx
from fastapi import HTTPException
from app.config import settings
import google.api_core.exceptions as google_exceptions 

# funcion para poder extraer texto de la respuesta de Gemini y normalizar todas sus respuetas 
def extract_text(data: dict) -> str:
    # 1. modelos nuevos: "text"
    if "text" in data and isinstance(data["text"], str):
        return data["text"]

    # 2. formato: "outputText"
    if "outputText" in data:
        return data["outputText"]

    # 3. modelos clásicos con candidates
    candidates = data.get("candidates", [])
    if candidates:
        cand = candidates[0]

        # parts dentro de content
        if "content" in cand and "parts" in cand["content"]:
            return "".join(p.get("text", "") for p in cand["content"]["parts"])

        # parts directos
        if "parts" in cand:
            return "".join(p.get("text", "") for p in cand["parts"])

    # 4. formato: content -> parts
    if "content" in data and "parts" in data["content"]:
        return "".join(p.get("text", "") for p in data["content"]["parts"])

    # 5. fallback final (por seguridad)
    return ""

class GeminiClient:
    def __init__(self, api_key: str = None, model: str = None, embedding_model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY no configurada en .env")
        self.model = model or settings.GEMINI_MODEL
        self.embedding_model = embedding_model or settings.GEMINI_EMBEDDING_MODEL
        self._headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
        }

    async def generate_text(
        self, 
        prompt: str, 
        max_tokens: int = 4096, 
        temperature: float = 0.3):

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
    
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=self._headers, json=payload)
                resp.raise_for_status()
                return extract_text(resp.json())

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Gemini API returned {e.response.status_code}: {e.response.text}"
            )

    # este metodo de la clase es para generar embeddings usando Gemini 
    async def embed_texts(self, texts: list[str]):
        if not isinstance(texts, list):
            texts = [texts]

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.embedding_model}:embedContent?key={self.api_key}"
        )

        embeddings = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for t in texts:
                payload = {
                    "content": {
                        "parts": [{"text": t}]
                    }
                }

                # REINTENTOS 429 APLICADOS POR TEXTO
                for attempt in range(5):
                    try:
                        resp = await client.post(url, headers=self._headers, json=payload)
                        resp.raise_for_status()
                        data = resp.json()
                        emb = data["embedding"]["values"]
                        embeddings.append(emb)
                        break  # salir del ciclo si tuvo éxito

                    except httpx.HTTPStatusError as e:
                        # Si es 429, hacer reintento exponencial
                        if e.response.status_code == 429:
                            wait_time = 2 ** attempt
                            print(f"[Gemini] 429 recibido. Reintentando en {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise RuntimeError(
                                f"Gemini API returned {e.response.status_code}: {e.response.text}"
                            )

                    except google_exceptions.ResourceExhausted:
                        wait_time = 2 ** attempt
                        print(f"[Gemini] 429 (Google) recibido. Reintentando en {wait_time}s...")
                        await asyncio.sleep(wait_time)

                else:
                    # Si nunca hizo break → falló después de 5 intentos
                    raise RuntimeError("Gemini API agotada incluso después de reintentos.")

        return embeddings
