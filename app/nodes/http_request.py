"""HttpRequest node definition."""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import requests

from app.constants.node_categories import CATEGORY_CORE
from app.constants.node_types import (
    ExecutionContext,
    ExecutionData,
    Node,
    NodeDescription,
)
from app.nodes.schemas.node_property import NodeProperty, NodePropertyOption


@dataclass
class HttpRequestDescription(NodeDescription):
    """Description for the HttpRequest node."""

    display_name: str = "HttpRequest"
    kind: str = "orcha-nodes.base.http_request"
    icon: str = "fa:globe"
    icon_color: str = "indigo"
    group: list = field(default_factory=lambda: ["core"])
    version: int = 1
    subtitle: str = "Make an HTTP request"
    description: str = "Makes an http request and returns the response data."
    defaults: Dict[str, Any] = field(default_factory=dict)
    credentials: list = field(default_factory=list)
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

    def execute(self, context: ExecutionContext) -> ExecutionData:
        """Execute the HTTP request based on parameters."""
        url = self.get_parsed_parameter("url", context) or ""
        method = self.parameters.get("method", "GET").upper()
        headers = self.get_parsed_parameter("headers", context) or {}
        body = self.get_parsed_parameter("body", context) or {}

        output = context.get_previous_output()

        if not url:
            output.error = "URL is required for HTTP request"
            return output

        try:
            request_kwargs = {
                "headers": headers if headers else None,
            }

            if method in ["POST", "PUT", "PATCH", "DELETE"]:
                if body:
                    if isinstance(body, dict):
                        request_kwargs["json"] = body
                    else:
                        request_kwargs["data"] = body

            response = requests.request(method, url, **request_kwargs)

            response_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
            }

            try:
                response_data["json"] = response.json()
            except (ValueError, requests.exceptions.JSONDecodeError):
                pass

            output.json[self.kind] = response_data

            if response.status_code >= 400:
                output.error = f"HTTP {response.status_code}: {response.reason}"

        except requests.exceptions.RequestException as e:
            output.error = f"HTTP request failed: {str(e)}"

        return output


NODE = Node(
    id="orcha-nodes.base.http_request",
    category=CATEGORY_CORE,
    description=HttpRequestDescription(),
)
