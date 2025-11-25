# backend/app/routes/chat.py

from fastapi import APIRouter, Depends, Header
from app.models.chat import ChatRequest, ChatResponse
from app.services.agent_service import CommercialAgentService

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    session_id: str = Header(default="default_session")
):
    agent = CommercialAgentService(session_id=session_id)
    response = await agent.answer(request.message)
    return ChatResponse(response=response)
