from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.routes import chat, whatsapp, admin, recommendation
from app.config import settings

app = FastAPI(
    title="Asistente Comercial Omnicanal",
    version="0.1.0",
)

# implementar rutas
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(recommendation.router, prefix="/recommendations", tags=["recommendations"])

# middleware basico 
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "Internal server error."}
    )

# endopoint para probar la funcion 
@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

# Crear tablas en arranque (solo en dev; en prod use migrations alembic)
def create_tables():
    from app.dependencies.db import engine
    from app.models.db_models import Base
    Base.metadata.create_all(bind=engine)

create_tables()
