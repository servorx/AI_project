# backend/app/routes/whatsapp.py
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import PlainTextResponse, JSONResponse
from app.config import settings
from app.services.whatsapp_service import WhatsAppService
from app.services.agent_service import CommercialAgentService
from app.dependencies.db import get_db
from sqlalchemy.orm import Session
from app.models.db_models import Conversation, Message
# para la parte de la actualización de datos del usuario
import re
import json
from app.services.user_service import UserService
import hashlib

router = APIRouter()

# GET verification
@router.get("/webhook")
def verify_token(request: Request):
    params = request.query_params

    challenge = params.get("hub.challenge")
    token = params.get("hub.verify_token")

    if token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge or "")
    
    return JSONResponse({"error": "Invalid verify token"}, status_code=403)

# POST receive messages
@router.post("/webhook")
async def receive_message(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    print("WA webhook body:", body)

    # validar estructura del webhook
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
    except:
        return JSONResponse({"status": "ignored"})

    # IGNORAR EVENTOS DE ESTADO (sent/delivered/read)
    if "statuses" in value:
        return JSONResponse({"status": "ignored_status"})

    messages = value.get("messages", [])
    if not messages:
        return JSONResponse({"status": "no_messages"})

    msg = messages[0]

    #  IGNORAR MENSAJES QUE NO SEAN TEXT O INTERACTIVE
    msg_type = msg.get("type")

    if msg_type not in ("text", "interactive"):
        return JSONResponse({"status": "ignored_non_text"})

    msg_id = msg.get("id")
    from_phone = msg.get("from")

    # IGNORAR MENSAJES DEL PROPIO BOT
    if from_phone == value["metadata"]["phone_number_id"]:
        return JSONResponse({"status": "ignored_self"})

    # PROTECCIÓN ANTI-DUPLICADOS (por ID)
    exists = db.query(Message).filter_by(external_id=msg_id).first()
    if exists:
        return JSONResponse({"status": "duplicate_ignored"})

    # 6. EXTRAER CONTENIDO DEL MENSAJE
    text = ""
    if msg_type == "text":
        text = msg["text"]["body"]
    elif msg_type == "interactive":
        interactive = msg["interactive"]
        if interactive["type"] == "button_reply":
            text = interactive["button_reply"].get("title")

    # HASH ANTI-DUPLICADOS (por contenido exacto)
    content_hash = hashlib.md5(text.encode()).hexdigest()

    dupe_text = db.query(Message).filter_by(
        conversation_id=from_phone,
        content_hash=content_hash
    ).first()

    if dupe_text:
        return JSONResponse({"status": "duplicate_text"})

    # CREAR O OBTENER CONVERSACIÓN
    session_id = from_phone

    conv = db.query(Conversation).filter_by(session_id=session_id).first()
    if not conv:
        conv = Conversation(session_id=session_id, user_phone=from_phone)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # 9. GUARDAR MENSAJE DEL USUARIO
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=text,
        external_id=msg_id,
        content_hash=content_hash
    )
    db.add(user_msg)
    db.commit()

    # ---------------------------------------------------------
    # 10. LLAMAR AL AGENTE
    # ---------------------------------------------------------
    agent_service = CommercialAgentService(session_id=session_id)
    try:
        resp_text = await agent_service.answer(text)
    except Exception as e:
        print("ERROR EN AGENTE WHATSAPP:", e)
        raise e

    # ---------------------------------------------------------
    # 11. DETECTAR <ACTION> (UPDATE PROFILE)
    # ---------------------------------------------------------
    pattern = r"<ACTION>(.*?)</ACTION>"
    match = re.search(pattern, resp_text, re.DOTALL)

    if match:
        try:
            action_json = match.group(1).strip()
            data = json.loads(action_json)

            if data.get("intent") == "update_profile":
                UserService.update_profile(db, from_phone, data.get("data", {}))

                clean_response = (
                    "¡Gracias por brindarme esta información! 😊 "
                    "Ahora puedo ayudarte mucho mejor. "
                    "¿Qué tipo de teclado mecánico estás buscando?"
                )

                # Guardar mensaje limpio del asistente
                assistant_msg = Message(
                    conversation_id=conv.id,
                    role="assistant",
                    content=clean_response
                )
                db.add(assistant_msg)
                db.commit()

                wa = WhatsAppService()
                await wa.send_text(to_phone=from_phone, text=clean_response)

                return {"status": "ok"}

        except Exception as e:
            print("ERROR PARSEANDO ACTION:", e)

    # ---------------------------------------------------------
    # 12. RESPUESTA NORMAL DEL AGENTE
    # ---------------------------------------------------------
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=resp_text
    )
    db.add(assistant_msg)
    db.commit()

    wa = WhatsAppService()
    await wa.send_text(to_phone=from_phone, text=resp_text)

    return {"status": "ok"}
