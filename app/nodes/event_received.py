"""Event Received node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any, List

from app.constants.node_categories import CATEGORY_TRIGGER
from app.constants.node_types import (
    ExecutionData,
    Node,
    NodeDescription,
)

from app.nodes.schemas.node_property import NodeProperty


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
    properties: List[NodeProperty] = field(
        default_factory=lambda: [
            NodeProperty(
                display_name="Event Type",
                name="event_type",
                type="string",
                default="",
                description="The name of the event to receive.",
            )
        ]
    )

    def execute(self, input: ExecutionData) -> ExecutionData:
        return input


NODE = Node(
    id="orcha-nodes.base.event_received",
    category=CATEGORY_TRIGGER,
    description=EventReceivedDescription(),
)
