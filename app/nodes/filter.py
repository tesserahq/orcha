"""Filter node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_categories import CATEGORY_FLOW
from app.constants.node_types import (
    ExecutionData,
    Node,
    NodeDescription,
    PropertyField,
)


@dataclass
class FilterDescription(NodeDescription):
    """Description for the Filter node."""

    displayName: str = "Filter"
    name: str = "filter"
    icon: str = "fa:filter"
    group: list = field(default_factory=lambda: ["flow"])
    version: int = 1
    subtitle: str = "Remove matching items"
    description: str = "Remove items matching a condition."
    defaults: Dict[str, Any] = field(default_factory=dict)
    inputs: list = field(default_factory=lambda: ["main"])
    outputs: list = field(default_factory=lambda: ["main"])
    credentials: list = field(default_factory=list)
    requestDefaults: Any = None
    properties: list = field(default_factory=list)

    def execute(self, input: ExecutionData) -> ExecutionData:
        return input


NODE = Node(
    id="orcha-nodes.base.filter",
    category=CATEGORY_FLOW,
    description=FilterDescription(),
)
