from app.agents.commercial_agent import CommercialAgent
from app.dependencies.gemini_client import GeminiClient
from fastapi import HTTPException

class CommercialAgentService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.gemini = GeminiClient()
        self.agent = CommercialAgent(session_id=self.session_id, gemini_client=self.gemini)

    async def answer(self, message: str) -> str:
        if not message or not message.strip():
            return "¿Puedes escribir tu pregunta con más detalle?"
        try:
            response = await self.agent.run(message)
            return response
        except Exception as e:
            # captura y transforma errores externos
            raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
