# backend/scripts/ingest_kb.py

import os
import asyncio
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.dependencies.gemini_client import GeminiClient
from app.config import settings


KB_DIR = os.path.join(os.path.dirname(__file__), "..", "kb")


async def ingest():
    print("=== Iniciando ingest de KB ===")
    print(f"Directorio KB: {KB_DIR}")

    # 1. Inicializar clientes
    gemini = GeminiClient()
    qdrant = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    # 2. Crear colección si no existe
    print("Validando colección company_kb...")

    vector_size = 768  # Gemini embedding models (ajustable según tu modelo)
    try:
        qdrant.get_collection(settings.COLLECTION_NAME)
        print("Colección ya existe.")
    except:
        print("Colección no existe. Creando...")
        qdrant.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE
            )
        )

    # 3. Leer archivos KB
    documents = []
    for fname in os.listdir(KB_DIR):
        if fname.endswith(".md") or fname.endswith(".txt"):
            path = os.path.join(KB_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append((fname, text))

    if not documents:
        print("No hay archivos en kb/. Nada para insertar.")
        return

    print(f"Documentos encontrados: {len(documents)}")

    # 4. Generar embeddings
    texts = [doc[1] for doc in documents]
    print("Generando embeddings con Gemini...")
    embeddings = await gemini.embed_texts(texts)

    # 5. Insertar en Qdrant
    print("Insertando documentos en Qdrant...")

    points = []
    for i, (fname, content) in enumerate(documents):
        payload = {
            "text": content,
            "filename": fname
        }

        points.append(
            qmodels.PointStruct(
                id=i + 1,
                vector=embeddings[i],
                payload=payload
            )
        )

    qdrant.upsert(
        collection_name=settings.COLLECTION_NAME,
        points=points
    )

    print("=== KB ingestado con éxito ===")


if __name__ == "__main__":
    asyncio.run(ingest())
