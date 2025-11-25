from fastapi import FastAPI
from app.routes import chat, whatsapp, admin
from app.config import settings

app = FastAPI(
    title="Asistente Comercial Omnicanal",
    version="0.1.0",
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

# Crear tablas en arranque (solo en dev; en prod use migrations alembic)
def create_tables():
    from app.dependencies.db import engine
    from app.models.db_models import Base
    Base.metadata.create_all(bind=engine)

create_tables()
