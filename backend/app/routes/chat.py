from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.models.chat_model import ChatRequest, ChatResponse
from app.services.agent_service import CommercialAgentService
from app.services.user_service import UserService
import json
from google.api_core import exceptions as google_exceptions

router = APIRouter()

# ahora recive el session_id desde el header
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    session_id: str = Header(default="session_web"),
    db: Session = Depends(get_db)
):
    agent = CommercialAgentService(session_id=session_id)

    try:
        agent_response = await agent.answer(request.message)
        # INTENT: update_profile
        try:
            # intenta convertir la respuesta del agente en JSON
            parsed = json.loads(agent_response)
            # si tiene el intent "update_profile", actualiza el perfil del usuario
            if parsed.get("intent") == "update_profile":
                phone = request.user_phone or request.session_id
                # actualiza el perfil del usuario en la base de datos
                try:
                    updated = UserService.update_profile(
                        db=db,
                        phone=phone,
                        data=parsed["data"]
                    )
                except ValueError as ve:
                    if str(ve) == "invalid_email":
                        return ChatResponse(response="Ese correo no es válido 😊 ¿Puedes revisarlo?")
                    if str(ve) == "invalid_address":
                        return ChatResponse(response="La dirección debe tener al menos 5 caracteres.")

                if not updated:
                    return ChatResponse(response="No encontré tu usuario para actualizar 🥲")

                return ChatResponse(response="Perfecto, ya tengo tu información 😊")
        except:
            pass
        # -------------------------------------

        return ChatResponse(response=agent_response)

    except google_exceptions.ResourceExhausted:
        raise HTTPException(
            status_code=503,
            detail="Gemini está saturado. Intenta de nuevo en unos segundos."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
