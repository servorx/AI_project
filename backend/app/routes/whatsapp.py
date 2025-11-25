# backend/app/routes/whatsapp.py
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import PlainTextResponse, JSONResponse
from app.config import settings
from app.services.whatsapp_service import WhatsAppService
from app.services.agent_service import CommercialAgentService
from app.dependencies.db import get_db
from sqlalchemy.orm import Session
from app.models.db_models import Conversation, Message
from app.utils.logger import log

router = APIRouter()

# GET verification
@router.get("/webhook")
def verify_token(mode: str = None, token: str = None, challenge: str = None):
    # Meta uses hub.mode, hub.verify_token, hub.challenge in some docs, other times different names
    # Accept both
    mode = mode or ""
    token = token or ""
    verify_token = settings.WHATSAPP_VERIFY_TOKEN

    if token == verify_token:
        # return challenge (raw)
        return PlainTextResponse(content=challenge or "", status_code=status.HTTP_200_OK)
    return JSONResponse({"status": "error", "message": "Invalid verify token"}, status_code=403)

# POST receive messages
@router.post("/webhook")
async def receive_message(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    log("whatsapp webhook body", body)

    # The webhook shape:
    # { "entry": [ { "changes":[{ "value": { "messages":[{...}], "metadata":{...} } }] } ] }
    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        metadata = value.get("metadata", {})
    except Exception as e:
        log("No message found in webhook", str(e))
        return JSONResponse({"status": "ignored"}, status_code=200)

    if not messages:
        return JSONResponse({"status": "no_messages"}, status_code=200)

    msg = messages[0]
    from_phone = msg.get("from")  # e.g. "57300...."
    text = None
    if msg.get("text"):
        text = msg["text"].get("body")
    elif msg.get("type") == "interactive":
        # handle button replies / interactive messages
        interactive = msg.get("interactive", {})
        if interactive.get("type") == "button_reply":
            text = interactive["button_reply"].get("title") or interactive["button_reply"].get("id")
    # fallback
    text = text or ""

    # Use session_id as phone number (simple)
    session_id = from_phone

    # Persist conversation & message
    conv = db.query(Conversation).filter_by(session_id=session_id).first()
    if not conv:
        conv = Conversation(session_id=session_id, user_phone=from_phone)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    message = Message(conversation_id=conv.id, role="user", content=text)
    db.add(message)
    db.commit()
    db.refresh(message)

    # Call agent
    agent_service = CommercialAgentService(session_id=session_id)
    # note: agent_service.answer is async
    try:
        resp_text = await agent_service.answer(text)
    except Exception as e:
        log("Error in agent", str(e))
        resp_text = "Lo siento, tuve un problema procesando tu mensaje. Intenta de nuevo más tarde."

    # Persist assistant message
    assistant_msg = Message(conversation_id=conv.id, role="assistant", content=resp_text)
    db.add(assistant_msg)
    db.commit()

    # Send response via WhatsApp
    wa = WhatsAppService()
    try:
        await wa.send_text(to_phone=from_phone, text=resp_text)
    except Exception as e:
        log("Error sending WA message", str(e))

    return JSONResponse({"status": "ok"}, status_code=200)
