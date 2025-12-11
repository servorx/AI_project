import httpx
from app.config import settings
from fastapi import HTTPException

GRAPH_BASE = "https://graph.facebook.com/v17.0"

class WhatsAppService:
    def __init__(self, phone_id: str = None, access_token: str = None):
        self.phone_id = phone_id or settings.WHATSAPP_PHONE_ID
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        if not self.phone_id or not self.access_token:
            raise RuntimeError("WHATSAPP_PHONE_ID o WHATSAPP_ACCESS_TOKEN no configurados")
        self.base_url = f"{GRAPH_BASE}/{self.phone_id}/messages"

    async def send_text(self, to_phone: str, text: str):
        payload = {"messaging_product": "whatsapp","to": to_phone,"type": "text","text": {"preview_url": False, "body": text}}
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(self.base_url, headers=headers, json=payload)
                res.raise_for_status()
                return res.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"WhatsApp API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Error sending WA message: {str(e)}")
