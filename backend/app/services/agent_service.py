from fastapi import HTTPException
from app.config import settings
from app.dependencies.gemini_client import GeminiClient
from app.agents.commercial_agent import CommercialAgent
from app.agents.langgraph_agent import LangGraphAgent

class CommercialAgentService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.gemini = GeminiClient()
        # Elegir implementación del agente
        if settings.USE_LANGGRAPH:
            print("Using LangGraphAgent as agent service.")
            self.agent = LangGraphAgent(
                session_id=self.session_id,
                gemini_client=self.gemini,
            )
        else:
            print("Using CommercialAgent as agent service.")
            self.agent = CommercialAgent(
                session_id=self.session_id,
                gemini_client=self.gemini,
            )
    # Envia un mensaje al agente y retorna su respuesta, incluyendo validaciones y manejo de errores
    async def answer(self, message: str) -> str:
        # Validación básica de entrada
        if not message or not message.strip():
            return "¿Puedes escribir tu pregunta con más detalle?"
        try:
            response = await self.agent.run(message)
            # Validación: el agente **SIEMPRE** debe devolver un string
            if not isinstance(response, str):
                raise ValueError(f"Respuesta inválida del agente: {response}")
            return response
        except HTTPException:
            # Si el agente ya lanzó una HTTPException, simplemente la propagamos
            raise
        except Exception as e:
            # Convertimos cualquier error técnico en HTTP 500
            raise HTTPException(
                status_code=500,
                detail=f"Agent error: {str(e)}"
            )
