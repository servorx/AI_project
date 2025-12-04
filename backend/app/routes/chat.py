from fastapi import APIRouter, Header, HTTPException
from app.models.chat_model import ChatRequest, ChatResponse
from app.services.agent_service import CommercialAgentService
from google.api_core import exceptions as google_exceptions

router = APIRouter()

# ahora recive el session_id desde el header
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    session_id: str = Header(default="session_web")
):
    # ahora pasamos session_id al servicio
    agent = CommercialAgentService(session_id=session_id)
    try:
        response = await agent.answer(request.message)
    except Exception as e:
        # log aquí
        raise HTTPException(status_code=500, detail=str(e))
    except google_exceptions.ResourceExhausted:
        raise HTTPException(
            status_code=503,
            detail="Gemini está saturado. Intenta de nuevo en unos segundos."
        )
    return ChatResponse(response=response)