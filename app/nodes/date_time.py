"""Date & Time node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_kinds import (
    CATEGORY_DATA_TRANSFORMATION,
    NodeDescription,
    Node,
    PropertyField,
)


@dataclass
class DateTimeDescription(NodeDescription):
    """Description for the Date & Time node."""

    displayName: str = "Date & Time"
    name: str = "dateTime"
    icon: str = "fa:clock"
    group: list = field(default_factory=lambda: ["data_transformation"])
    version: int = 1
    subtitle: str = "Manipulate dates"
    description: str = "Manipulate date and time values."
    defaults: Dict[str, Any] = field(default_factory=dict)
    inputs: list = field(default_factory=lambda: ["main"])
    outputs: list = field(default_factory=lambda: ["main"])
    credentials: list = field(default_factory=list)
    requestDefaults: Any = None
    properties: list = field(default_factory=list)


NODE = Node(
    id="orcha-nodes.base.date_time",
    category=CATEGORY_DATA_TRANSFORMATION,
    description=DateTimeDescription(),
)
