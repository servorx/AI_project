import os
import asyncio
# esto se importa con el fin de imprimir informacion relevante
import traceback
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse

from app.dependencies.gemini_client import GeminiClient
from app.config import settings

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "kb")

async def ingest():
    # se envuelve en un try/except para que se pueda capturar y imprimir la excepción
    try:
        print("=== Iniciando ingest de KB ===")
        print(f"Directorio KB: {KB_DIR}")
        print(f"QDRANT_URL={settings.QDRANT_URL} QDRANT_COLLECTION={settings.QDRANT_COLLECTION}")

        gemini = GeminiClient()
        qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, https=False)

        # validar colección
        try:
            cols = [c.name for c in qdrant.get_collections().collections]
            print("Collections on server:", cols)
            if settings.QDRANT_COLLECTION not in cols:
                print("Colección no existe. Creando...")
                qdrant.create_collection(
                    collection_name=settings.QDRANT_COLLECTION,
                    vectors_config=qmodels.VectorParams(size=768, distance=qmodels.Distance.COSINE)
                )
                print("Colección creada.")
            else:
                print("Colección ya existe.")
        except Exception as e:
            print("Error validando / creando colección:", e)
            raise

        # leer archivos
        documents = []
        for fname in os.listdir(KB_DIR):
            if fname.endswith(".md") or fname.endswith(".txt"):
                path = os.path.join(KB_DIR, fname)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if text:
                        documents.append((fname, text))

        print(f"Documentos detectados: {len(documents)}")
        if not documents:
            print("No hay docs en kb/. Fin.")
            return

        texts = [d[1] for d in documents]
        print("Generando embeddings (longitud textos):", len(texts))
        embeddings = await gemini.embed_texts(texts)
        print("Embeddings obtenidos:", len(embeddings))

        if len(embeddings) != len(texts):
            raise RuntimeError("Embeddings length mismatch")

        points = []
        for i, (fname, content) in enumerate(documents):
            points.append(
                qmodels.PointStruct(
                    id=i + 1,
                    vector=embeddings[i],
                    payload={"text": content, "filename": fname}
                )
            )

        print("Upsertando puntos:", len(points))
        res = qdrant.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
        print("Upsert response:", res)
        print("Count after upsert:", qdrant.count(collection_name=settings.QDRANT_COLLECTION))
        print("=== KB ingestado con éxito ===")
    except Exception:
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(ingest())
