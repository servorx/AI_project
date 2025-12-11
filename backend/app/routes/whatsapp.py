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

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])
    except:
        return JSONResponse({"status": "ignored"})

    if not messages:
        return JSONResponse({"status": "no_messages"})

    msg = messages[0]
    msg_id = msg.get("id")
    from_phone = msg.get("from")

    # Evitar duplicados (muy importante)
    exists = db.query(Message).filter_by(external_id=msg_id).first()
    if exists:
        return JSONResponse({"status": "duplicate_ignored"})

    text = ""
    if msg.get("text"):
        text = msg["text"]["body"]
    elif msg.get("type") == "interactive":
        interactive = msg["interactive"]
        if interactive["type"] == "button_reply":
            text = interactive["button_reply"].get("title")

    # Crear conversación si no existe
    session_id = from_phone

    conv = db.query(Conversation).filter_by(session_id=session_id).first()
    if not conv:
        conv = Conversation(session_id=session_id, user_phone=from_phone)
        db.add(conv)
        db.commit()
        db.refresh(conv)
    # PARSER DE <ACTION> PARA UPDATE_PROFILE
    pattern = r"<ACTION>(.*?)</ACTION>"
    match = re.search(pattern, resp_text, re.DOTALL)

    if match:
        try:
            # Extraer JSON
            action_json = match.group(1).strip()
            data = json.loads(action_json)

            # PROCESO DE ACTUALIZACIÓN
            if data.get("intent") == "update_profile":
                UserService.update_profile(db, from_phone, data.get("data", {}))

                # Guardar mensaje del asistente sin el JSON
                assistant_msg = Message(
                    conversation_id=conv.id,
                    role="assistant",
                    content="¡Gracias por brindarme esta información! 😊 Ahora puedo ayudarte mucho mejor. ¿Qué tipo de teclado mecánico estás buscando?"
                )
                db.add(assistant_msg)
                db.commit()

                # Enviar mensaje limpio al usuario
                wa = WhatsAppService()
                await wa.send_text(
                    to_phone=from_phone,
                    text="¡Gracias por brindarme esta información! 😊 Ahora puedo ayudarte mucho mejor. ¿Qué tipo de teclado mecánico estás buscando?"
                )

                return {"status": "ok"}

        except Exception as e:
            print("ERROR PARSEANDO ACTION:", e)
            # si falla, simplemente continúa con flujo normal
            pass

    # ---------------------------------------------------------
    # SI NO HAY <ACTION> → RESPUESTA NORMAL
    # ---------------------------------------------------------

    # Guardar mensaje del usuario
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=text,
        external_id=msg_id
    )
    db.add(user_msg)
    db.commit()

    # Llamar agente
    agent_service = CommercialAgentService(session_id=session_id)
    try:
        resp_text = await agent_service.answer(text)
    except Exception as e:
        print("ERROR EN AGENTE WHATSAPP:", e)
        raise e  # deja que FastAPI te muestre el error real en consola

    # Guardar respuesta del asistente
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=resp_text
    )
    db.add(assistant_msg)
    db.commit()

    # Enviar WhatsApp
    wa = WhatsAppService()
    await wa.send_text(to_phone=from_phone, text=resp_text)

    return {"status": "ok"}
