from fastapi import APIRouter, Request
from app.utils.logger import log

router = APIRouter()

@router.get("/webhook")
def verify_token(mode: str, token: str, challenge: str):
    VERIFY_TOKEN = "test_token"  # mover a settings si quieres

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"status": "error"}

@router.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    log("Webhook recibido", body)
    return {"status": "received"}
