import asyncio
import httpx
from fastapi import HTTPException
from app.config import settings
import google.api_core.exceptions as google_exceptions 

BASE_URL = "https://generativeai.googleapis.com/v1"

class GeminiClient:
    def __init__(self, api_key: str = None, model: str = None, embedding_model: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY no configurada en .env")
        self.model = model or settings.GEMINI_MODEL
        self.embedding_model = embedding_model or settings.GEMINI_EMBEDDING_MODEL
        self._headers = {
            "Content-Type": "application/json",
        }

    async def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature
                }
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=self._headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Gemini API returned {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Error calling Gemini: {str(e)}")

        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            text = "".join(p.get("text", "") for p in parts)
            return text
        return data.get("outputText") or data.get("text") or ""
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

                # 🔥 REINTENTOS 429 APLICADOS POR TEXTO
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
