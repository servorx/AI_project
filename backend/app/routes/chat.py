from fastapi import APIRouter, Depends
from app.models.chat_model import ChatRequest, ChatResponse
from app.services.agent_service import CommercialAgentService

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    agent = CommercialAgentService()
    response = await agent.answer(request.message)
    return ChatResponse(response=response)
