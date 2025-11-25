import httpx
from app.config import settings

# TODO: revisar si es necesario cambiar esto por otra ruta
GRAPH_BASE = "https://graph.facebook.com/v17.0"

class WhatsAppService:
    def __init__(self, phone_id: str = None, access_token: str = None):
        self.phone_id = phone_id or settings.WHATSAPP_PHONE_ID
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.base_url = f"{GRAPH_BASE}/{self.phone_id}/messages"

    async def send_text(self, to_phone: str, text: str):
        """
        to_phone: phone number in international format, e.g. 573001112233
        """
        if not self.phone_id or not self.access_token:
            raise RuntimeError("WHATSAPP_PHONE_ID or WHATSAPP_ACCESS_TOKEN not configured")

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": False, "body": text}
        }
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
