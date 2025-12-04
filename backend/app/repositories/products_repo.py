from app.models.product_model import Product
from app.models.guide_model import Guide

# TODO: reemplazar por una implementación real de una base de datos y no mock
MOCK_PRODUCTS = [
    Product(
        id=1,
        name="Keychron K6",
        description="Teclado 65% ideal para programar, compacto y hot-swap.",
        price=89,
        switch="Brown",
        image="/static/k6.png"
    ),
    Product(
        id=2,
        name="Royal Kludge RK84",
        description="TKL inalámbrico, excelente calidad/precio.",
        price=65,
        switch="Red",
        image="/static/rk84.png"
    ),
]

MOCK_GUIDES = [
    Guide(
        title="¿Qué es un switch?",
        content="Es el mecanismo debajo de cada tecla que define la sensación al escribir."
    ),
    Guide(
        title="Formatos de teclado",
        content="Full-size, TKL, 75%, 65%, 60%. Cada uno elimina secciones para ahorrar espacio."
    ),
]

async def get_all_products():
    return MOCK_PRODUCTS

async def get_all_guides():
    return MOCK_GUIDES
