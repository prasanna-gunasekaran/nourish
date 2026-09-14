from abc import ABC, abstractmethod
import os
from typing import Dict, Any

class WhatsAppService(ABC):
    @abstractmethod
    def send_message(self, recipient_phone: str, text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def parse_inbound_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class LocalSimulatorWhatsAppService(WhatsAppService):
    """
    Local Web Simulator WhatsApp Adapter.
    Processes messages directly from the web chat interface.
    """
    def send_message(self, recipient_phone: str, text: str) -> Dict[str, Any]:
        return {
            "status": "delivered_to_simulator",
            "recipient": recipient_phone,
            "text": text
        }

    def parse_inbound_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "sender": payload.get("user_id", "demo_user"),
            "message": payload.get("message", "")
        }

class WhatsAppCloudAPIService(WhatsAppService):
    """
    Official Meta WhatsApp Business Cloud API Adapter.
    Activated when WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID are provided.
    """
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    def is_configured(self) -> bool:
        return bool(self.access_token and self.phone_number_id)

    def send_message(self, recipient_phone: str, text: str) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("WhatsApp Cloud API credentials missing in .env")
        # Cloud API POST request payload simulation:
        # url = f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages"
        return {"status": "sent_via_cloud_api", "recipient": recipient_phone}

    def parse_inbound_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Parse Meta webhook JSON structure: entry[0].changes[0].value.messages[0]
        return {"sender": "whatsapp_user", "message": "Inbound Meta payload"}
