from app.connectors.http_request import HttpRequestConnector
from app.connectors.telegram_message import TelegramMessageConnector

# Add new connectors here as you build them.
CONNECTOR_REGISTRY = {
    "http_request": HttpRequestConnector(),
    "telegram_message": TelegramMessageConnector(),
}
