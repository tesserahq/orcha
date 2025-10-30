"""HttpRequest node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any

from app.constants.node_kinds import (
    CATEGORY_CORE,
    NodeDescription,
    Node,
    PropertyField,
)


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
    properties: list = field(default_factory=list)


NODE = Node(
    id="orcha-nodes.base.http_request",
    category=CATEGORY_CORE,
    description=HttpRequestDescription(),
)
