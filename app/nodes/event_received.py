"""Event Received node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any, List

from app.constants.node_categories import CATEGORY_TRIGGER
from app.constants.node_types import (
    ExecutionContext,
    ExecutionData,
    Node,
    NodeDescription,
)

from app.nodes.schemas.node_property import NodeProperty

EVENT_RECEIVED_NODE_ID = "orcha-nodes.base.event_received"


@dataclass
class EventReceivedDescription(NodeDescription):
    """Description for the Event Received node."""

    display_name: str = "Event Received"
    kind: str = EVENT_RECEIVED_NODE_ID
    icon: str = "fa:calendar-check"
    icon_color: str = "indigo"
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

    def execute(self, context: ExecutionContext) -> ExecutionData:
        # If a real trigger event exists (event-triggered run), output it as json.
        if context.trigger_event:
            return ExecutionData(json=context.trigger_event)

        # No trigger event — manual run. Fall back to the configured test payload.
        test_payload = self.parameters.get("event_test_payload")
        if not test_payload:
            return ExecutionData(
                json={}, error="No event or event test payload provided"
            )

        return ExecutionData(json=test_payload)


NODE = Node(
    id=EVENT_RECEIVED_NODE_ID,
    category=CATEGORY_TRIGGER,
    description=EventReceivedDescription(),
)
