from fastapi import FastAPI, HTTPException
# arreglar CORS
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes import chat, whatsapp, admin, recommendation, user, message
from app.config import settings
from app.dependencies.db import create_tables

app = FastAPI(
    title="Asistente Comercial Omnicanal",
    version="0.1.0",
)

# implementar rutas
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(recommendation.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(message.router, prefix="/messages", tags=["messages"])

# middleware basico 
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "Internal server error."}
    )
# configurar CORS
app.add_middleware(
    CORSMiddleware,
    # el * solo mientras desarrollo
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# endpoint para probar que el backend está funcionando
@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}

# Crear tablas en arranque (solo en dev; en prod use migrations alembic)
create_tables()
