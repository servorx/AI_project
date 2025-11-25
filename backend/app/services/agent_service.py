from app.agents.commercial_agent import CommercialAgent
from app.dependencies.gemini_client import GeminiClient

class CommercialAgentService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.gemini = GeminiClient()
        self.agent = CommercialAgent(session_id=self.session_id, gemini_client=self.gemini)

    async def answer(self, message: str) -> str:
        return await self.agent.run(message)
