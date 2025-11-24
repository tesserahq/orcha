"""HttpRequest node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any, List

from app.constants.node_categories import CATEGORY_CORE
from app.constants.node_types import (
    ExecutionData,
    Node,
    NodeDescription,
    PropertyField,
)
from app.nodes.schemas.node_property import NodeProperty, NodePropertyOption


@dataclass
class HttpRequestDescription(NodeDescription):
    """Description for the HttpRequest node."""

    displayName: str = "HttpRequest"
    name: str = "httpRequest"
    icon: str = "fa:globe"
    group: list = field(default_factory=lambda: ["core"])
    version: int = 1
    subtitle: str = "Make an HTTP request"
    description: str = "Makes an http request and returns the response data."
    defaults: Dict[str, Any] = field(default_factory=dict)
    inputs: list = field(default_factory=lambda: ["main"])
    outputs: list = field(default_factory=lambda: ["main"])
    credentials: list = field(default_factory=list)
    requestDefaults: Any = None
    properties: List[NodeProperty] = field(
        default_factory=lambda: [
            NodeProperty(
                display_name="URL",
                name="url",
                type="string",
                default="",
                description="The URL to make the request to.",
            ),
            NodeProperty(
                display_name="Method",
                name="method",
                type="options",
                options=[
                    NodePropertyOption(name="GET", value="GET"),
                    NodePropertyOption(name="POST", value="POST"),
                    NodePropertyOption(name="PUT", value="PUT"),
                    NodePropertyOption(name="DELETE", value="DELETE"),
                    NodePropertyOption(name="PATCH", value="PATCH"),
                    NodePropertyOption(name="HEAD", value="HEAD"),
                    NodePropertyOption(name="OPTIONS", value="OPTIONS"),
                ],
                default="GET",
                description="The HTTP method to use for the request.",
            ),
            NodeProperty(
                display_name="Headers",
                name="headers",
                type="json",
                default={},
                description="The headers to send with the request.",
            ),
            NodeProperty(
                display_name="Body",
                name="body",
                type="json",
                default={},
                description="The body to send with the request.",
            ),
        ]
    )

    def execute(self, input: ExecutionData) -> ExecutionData:
        return input


NODE = Node(
    id="orcha-nodes.base.http_request",
    category=CATEGORY_CORE,
    description=HttpRequestDescription(),
)
