from fastapi import APIRouter, Depends, Header
from app.models.chat_model import ChatRequest, ChatResponse
from app.services.agent_service import CommercialAgentService

router = APIRouter()

# ahora recive el session_id desde el header
@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    session_id: str = Header(default="web_default")
):
    agent = CommercialAgentService(session_id=session_id)
    response = await agent.answer(request.message)
    return ChatResponse(response=response)