"""Test Action node definition.

This is a test-only node used for testing workflows.
It simply passes through the input data without modification.
"""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_categories import CATEGORY_CORE
from app.constants.node_types import (
    ExecutionData,
    Node,
    NodeDescription,
)


@dataclass
class TestActionDescription(NodeDescription):
    """Description for the Test Action node."""

    display_name: str = "Test Action"
    kind: str = "orcha-nodes.base.test_action"
    icon: str = "fa:flask"
    icon_color: str = "indigo"
    group: list = field(default_factory=lambda: ["core"])
    version: int = 1
    subtitle: str = "Test node for workflows"
    description: str = (
        "A simple test node that passes through data. Used for testing only."
    )
    defaults: Dict[str, Any] = field(default_factory=dict)
    credentials: list = field(default_factory=list)
    properties: list = field(default_factory=list)

    def execute(self, input: ExecutionData) -> ExecutionData:
        """Execute the test action node - simply passes through the input data."""
        return input


NODE = Node(
    id="orcha-nodes.base.test_action",
    category=CATEGORY_CORE,
    description=TestActionDescription(),
)
