"""Edit Fields node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_categories import CATEGORY_DATA_TRANSFORMATION
from app.constants.node_types import (
    ExecutionData,
    Node,
    NodeDescription,
    PropertyField,
)


@dataclass
class EditFieldsDescription(NodeDescription):
    """Description for the Edit Fields node."""

    displayName: str = "Edit Fields"
    kind: str = "orcha-nodes.base.edit_fields"
    icon: str = "fa:edit"
    group: list = field(default_factory=lambda: ["data_transformation"])
    version: int = 1
    subtitle: str = "Modify item fields"
    description: str = "Modify, add, or remove item fields."
    defaults: Dict[str, Any] = field(default_factory=dict)
    inputs: list = field(default_factory=lambda: ["main"])
    outputs: list = field(default_factory=lambda: ["main"])
    credentials: list = field(default_factory=list)
    requestDefaults: Any = None
    properties: list = field(default_factory=list)

    def execute(self, input: ExecutionData) -> ExecutionData:
        return input


NODE = Node(
    id="orcha-nodes.base.edit_fields",
    category=CATEGORY_DATA_TRANSFORMATION,
    description=EditFieldsDescription(),
)
