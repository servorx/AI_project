import langroid as lr
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.rag_service import RAGService

def build_agent():

    rag = RAGService()

    class CommercialAgent(lr.Agent):
        async def run(self, message: str) -> str:
            # RAG → obtener contexto
            results = rag.retrieve(message)
            kb_context = "\n".join([r.payload.get("text", "") for r in results])

            prompt = f"""
{SYSTEM_PROMPT}

Contexto recuperado:
{kb_context}

Mensaje del usuario:
{message}
"""

            response = await self.llm.apredict(prompt)
            return response

    return CommercialAgent()
