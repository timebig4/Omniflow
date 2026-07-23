from typing import Any, Dict

import httpx

from app.connectors.base import Connector


def render(value: Any, context: Dict[str, Any]) -> Any:
    """Very small templating: replaces "{{trigger.foo.bar}}" style paths
    with values pulled out of context. Keeps things simple and dependency
    free; swap for Jinja2 later if you need more power.
    """
    if isinstance(value, str) and "{{" in value:
        out = value
        import re

        for match in re.findall(r"{{\s*([\w\.]+)\s*}}", value):
            parts = match.split(".")
            node = context
            for p in parts:
                if isinstance(node, dict) and p in node:
                    node = node[p]
                else:
                    node = None
                    break
            out = out.replace("{{ " + match + " }}", str(node)).replace(
                "{{" + match + "}}", str(node)
            )
        return out
    if isinstance(value, dict):
        return {k: render(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [render(v, context) for v in value]
    return value


class HttpRequestConnector(Connector):
    """The universal action: call any URL with any method/body/headers.

    Step config example:
    {
        "url": "https://hooks.example.com/xyz",
        "method": "POST",
        "headers": {"Authorization": "Bearer {{trigger.token}}"},
        "body": {"text": "New event: {{trigger.title}}"}
    }
    """

    def run(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        url = render(config["url"], context)
        method = config.get("method", "POST").upper()
        headers = render(config.get("headers", {}), context)
        body = render(config.get("body", {}), context)

        with httpx.Client(timeout=15) as client:
            resp = client.request(method, url, headers=headers, json=body)

        return {
            "status_code": resp.status_code,
            "response_text": resp.text[:2000],  # keep run logs bounded
        }
