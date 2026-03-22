"""Date & Time node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_categories import CATEGORY_DATA_TRANSFORMATION
from app.constants.node_types import (
    ExecutionContext,
    ExecutionData,
    Node,
    NodeDescription,
)


@dataclass
class DateTimeDescription(NodeDescription):
    """Description for the Date & Time node."""

    display_name: str = "Date & Time"
    kind: str = "orcha-nodes.base.date_time"
    icon: str = "fa:clock"
    icon_color: str = "indigo"
    group: list = field(default_factory=lambda: ["data_transformation"])
    version: int = 1
    subtitle: str = "Manipulate dates"
    description: str = "Manipulate date and time values."
    defaults: Dict[str, Any] = field(default_factory=dict)
    credentials: list = field(default_factory=list)
    properties: list = field(default_factory=list)

    def execute(self, context: ExecutionContext) -> ExecutionData:
        return context.get_previous_output()


NODE = Node(
    id="orcha-nodes.base.date_time",
    category=CATEGORY_DATA_TRANSFORMATION,
    description=DateTimeDescription(),
)
