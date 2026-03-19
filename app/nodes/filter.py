"""Filter node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_categories import CATEGORY_FLOW
from app.constants.node_types import (
    ExecutionContext,
    ExecutionData,
    Node,
    NodeDescription,
)


@dataclass
class FilterDescription(NodeDescription):
    """Description for the Filter node."""

    display_name: str = "Filter"
    kind: str = "orcha-nodes.base.filter"
    icon: str = "fa:filter"
    icon_color: str = "indigo"
    group: list = field(default_factory=lambda: ["flow"])
    version: int = 1
    subtitle: str = "Remove matching items"
    description: str = "Remove items matching a condition."
    defaults: Dict[str, Any] = field(default_factory=dict)
    credentials: list = field(default_factory=list)
    properties: list = field(default_factory=list)

    def execute(self, context: ExecutionContext) -> ExecutionData:
        return context.get_previous_output()


NODE = Node(
    id="orcha-nodes.base.filter",
    category=CATEGORY_FLOW,
    description=FilterDescription(),
)
