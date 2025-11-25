from app.agents.commercial_agent import build_agent

class CommercialAgentService:

    def __init__(self):
        self.agent = build_agent()

    async def answer(self, message: str) -> str:
        return await self.agent.run(message)
