from collections import defaultdict, deque

# Memoria en RAM (suficiente para el MVP)
# { session_id: deque([{"role": "user/assistant", "text": "..."}, ...]) }
CONVERSATION_MEMORY = defaultdict(lambda: deque(maxlen=6)) 
# memoria máxima = últimos 6 mensajes

class MemoryService:

    @staticmethod
    def add_message(session_id: str, role: str, text: str):
        CONVERSATION_MEMORY[session_id].append({
            "role": role,
            "text": text
        })

    @staticmethod
    def get_memory(session_id: str):
        return list(CONVERSATION_MEMORY[session_id])
