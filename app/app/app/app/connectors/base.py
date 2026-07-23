from abc import ABC, abstractmethod
from typing import Any, Dict


class Connector(ABC):
    """Base class for every action Omniflow can run as a workflow step.

    To add a new integration (Slack, Discord, Gmail, Notion, ...):
      1. Subclass Connector, implement `run`.
      2. Register it in connectors/registry.py under a short key.
      3. Reference that key as `connector_type` on a Step.

    `context` carries data forward between steps: it starts as the
    trigger payload and each step's return value is merged in under
    that step's order index, so later steps can reference earlier
    results via config templating (see engine/executor.py).
    """

    @abstractmethod
    def run(self, config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        ...
