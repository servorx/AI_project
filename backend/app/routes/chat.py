from fastapi import APIRouter, Header, HTTPException
from app.models.chat_model import ChatRequest, ChatResponse
from app.services.agent_service import CommercialAgentService

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
    return ChatResponse(response=response)