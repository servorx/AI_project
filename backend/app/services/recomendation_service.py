from app.repositories.products_repo import get_all_products, get_all_guides
from app.services.rag_service import RAGService
from app.models.product_model import Product
from typing import List, Dict, Any

# generar una instancia de RAG
rag = RAGService()

async def get_recommendations() -> Dict[str, Any]:
    # 1. Extraer preferencias del usuario desde la KB (últimos mensajes vectorizados)
    preferences = await rag.extract_preferences()

    # 2. Obtener catálogos locales
    products: List[Product] = await get_all_products()
    guides = await get_all_guides()

    # 3. Aplicar reglas simples (luego puedes meter ML o razonamiento LLM)
    ranked = rank_products(products, preferences)

    return {
        "preferences_detected": preferences,
        "products": ranked,
        "guides": guides,
    }


def rank_products(products: List[Product], prefs: Dict[str, Any]):
    if not prefs:
        return products

    score_map = []

    for p in products:
        score = 0

        # Ejemplo de reglas según preferencias:
        if prefs.get("format") and prefs["format"] in p.name.lower():
            score += 3

        if prefs.get("switch") and p.switch and prefs["switch"].lower() in p.switch.lower():
            score += 2

        if prefs.get("budget") and p.price <= prefs["budget"]:
            score += 1

        score_map.append((score, p))

    # ordenar por score descendente
    score_map.sort(key=lambda x: x[0], reverse=True)

    return [p for _, p in score_map]
