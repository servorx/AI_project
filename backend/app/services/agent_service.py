from app.agents.commercial_agent import CommercialAgent
from app.dependencies.gemini_client import GeminiClient

class CommercialAgentService:
    def __init__(self, gemini_client: GeminiClient = None):
        self.gemini = gemini_client or GeminiClient()
        self.agent = CommercialAgent(gemini_client=self.gemini)

    async def answer(self, message: str) -> str:
        return await self.agent.run(message)
