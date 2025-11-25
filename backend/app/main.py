from fastapi import FastAPI
from app.routers import chat, whatsapp
from app.config import settings

app = FastAPI(
    title="Asistente Comercial Omnicanal",
    version="0.1.0",
)

# Routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV}
