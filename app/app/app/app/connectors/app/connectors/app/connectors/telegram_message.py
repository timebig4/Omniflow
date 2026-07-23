from typing import Any, Dict

import httpx

from app.config import settings
from app.connectors.base import Connector
from app.connectors.http_request import render


class TelegramMessageConnector(Connector):
    """Sends a message to a chat via the bot. Config:
    {"chat_id": "<tenant telegram_user_id>", "text": "Run finished: {{trigger.status}}"}
    """

    def run(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        chat_id = render(config["chat_id"], context)
        text = render(config["text"], context)

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        with httpx.Client(timeout=15) as client:
            resp = client.post(url, json={"chat_id": chat_id, "text": text})

        return {"status_code": resp.status_code}
