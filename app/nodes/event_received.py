"""Event Received node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_categories import (
    CATEGORY_TRIGGER,
    ExecutionData,
    NodeDescription,
    Node,
    PropertyField,
)


@dataclass
class EventReceivedDescription(NodeDescription):
    """Description for the Event Received node."""

    displayName: str = "Event Received"
    name: str = "eventReceived"
    icon: str = "fa:calendar-check"
    group: list = field(default_factory=lambda: ["trigger"])
    version: int = 1
    subtitle: str = "Trigger workflow on event"
    description: str = "Trigger a workflow when a matching event is received."
    defaults: Dict[str, Any] = field(default_factory=dict)
    inputs: list = field(default_factory=list)
    outputs: list = field(default_factory=lambda: ["main"])
    credentials: list = field(default_factory=list)
    requestDefaults: Any = None
    properties: list = field(default_factory=list)

    def execute(self, input: ExecutionData) -> ExecutionData:
        return input


NODE = Node(
    id="orcha-nodes.base.event_received",
    category=CATEGORY_TRIGGER,
    description=EventReceivedDescription(),
)
