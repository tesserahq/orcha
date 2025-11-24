"""If node definition."""

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
class IfDescription(NodeDescription):
    """Description for the If node."""

    displayName: str = "If"
    name: str = "if"
    icon: str = "fa:code-branch"
    group: list = field(default_factory=lambda: ["flow"])
    version: int = 1
    subtitle: str = "Route items conditionally"
    description: str = "Route items to different branches (true/false)."
    defaults: Dict[str, Any] = field(default_factory=dict)
    inputs: list = field(default_factory=lambda: ["main"])
    outputs: list = field(default_factory=lambda: ["true", "false"])
    credentials: list = field(default_factory=list)
    requestDefaults: Any = None
    properties: list = field(default_factory=list)

    def execute(self, input: ExecutionData) -> ExecutionData:
        return input


NODE = Node(
    id="orcha-nodes.base.if",
    category=CATEGORY_FLOW,
    description=IfDescription(),
)
