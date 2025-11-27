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
from app.schemas.event import EventBase as EventSchema


@dataclass
class EventReceivedDescription(NodeDescription):
    """Description for the Event Received node."""

    display_name: str = "Event Received"
    kind: str = "orcha-nodes.base.event_received"
    icon: str = "fa:calendar-check"
    group: list = field(default_factory=lambda: ["trigger"])
    version: int = 1
    subtitle: str = "Trigger workflow on event"
    description: str = "Trigger a workflow when a matching event is received."
    defaults: Dict[str, Any] = field(default_factory=dict)
    credentials: list = field(default_factory=list)
    properties: List[NodeProperty] = field(
        default_factory=lambda: [
            NodeProperty(
                display_name="Event Type",
                name="event_type",
                type="string",
                default="",
                description="The name of the event to receive.",
            ),
            NodeProperty(
                display_name="Event Example Payload",
                name="event_test_payload",
                type="json",
                default="",
                description="The example payload of the event to receive. This is used to test the event receiver.",
            ),
        ]
    )

    def execute(self, input: ExecutionData) -> ExecutionData:
        # If there is no event that triggered this node, we can asume it's a manual trigger.
        # So we need to check if the property event_test_payload is set. Otherwise we return an error.
        if not input.has_event():
            if not self.parameters.get("event_test_payload"):
                input.error = "No event or event test payload provided"
                return input
            else:
                input.event = EventSchema(**self.parameters.get("event_test_payload"))
                return input

        return input


NODE = Node(
    id="orcha-nodes.base.event_received",
    category=CATEGORY_TRIGGER,
    description=EventReceivedDescription(),
)
