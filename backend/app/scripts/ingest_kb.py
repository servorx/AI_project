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
    logs = []  # <-- buffer donde guardamos los logs

    def log(msg):
        print(msg)      # sigue imprimiendo en consola
        logs.append(msg)  # además lo guardamos para el endpoint

    try:
        log("=== Iniciando ingest de KB ===")
        log(f"Directorio KB: {KB_DIR}")
        log(f"QDRANT_URL={settings.QDRANT_URL} QDRANT_COLLECTION={settings.QDRANT_COLLECTION}")

        gemini = GeminiClient()
        qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, https=False)

        cols = [c.name for c in qdrant.get_collections().collections]
        log(f"Collections on server: {cols}")

        if settings.QDRANT_COLLECTION not in cols:
            log("Colección no existe. Creando...")
            qdrant.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=qmodels.VectorParams(size=768, distance=qmodels.Distance.COSINE)
            )
            log("Colección creada.")
        else:
            log("Colección ya existe.")

        # leer docs
        documents = []
        for fname in os.listdir(KB_DIR):
            if fname.endswith(".md") or fname.endswith(".txt"):
                path = os.path.join(KB_DIR, fname)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if text:
                        documents.append((fname, text))

        log(f"Documentos detectados: {len(documents)}")
        if not documents:
            log("No hay docs en kb/. Fin.")
            return "\n".join(logs)

        texts = [d[1] for d in documents]
        log(f"Generando embeddings (longitud textos): {len(texts)}")

        embeddings = await gemini.embed_texts(texts)
        log(f"Embeddings obtenidos: {len(embeddings)}")

        points = []
        for i, (fname, content) in enumerate(documents):
            points.append(
                qmodels.PointStruct(
                    id=i+1,
                    vector=embeddings[i],
                    payload={"text": content, "filename": fname}
                )
            )

        log(f"Upsertando puntos: {len(points)}")
        res = qdrant.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points
        )
        log(f"Upsert response: {res}")

        count = qdrant.count(collection_name=settings.QDRANT_COLLECTION)
        log(f"Count after upsert: {count}")

        log("=== KB ingestado con éxito ===")
        return "\n".join(logs)

    except Exception:
        traceback.print_exc()
        logs.append(traceback.format_exc())
        return "\n".join(logs)


# si el modulo se ejecuta directamente, ejecutar ingest
if __name__ == "__main__":
    asyncio.run(ingest())
