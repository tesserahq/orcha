"""Sendly node definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.constants.node_categories import CATEGORY_ACTION_APP
from app.constants.node_types import ExecutionData, Node, NodeDescription
from app.nodes.schemas.node_property import (
    DisplayOptions,
    NodeProperty,
    NodePropertyOption,
    StringTypeOptions,
)


@dataclass
class SendlyDescription(NodeDescription):
    """Description for the Sendly node."""

    display_name: str = "Sendly"
    kind: str = "orcha-nodes.sendly"
    icon: str = "fa:envelope"
    icon_color: str = "blue"
    group: list = field(default_factory=lambda: ["action_app"])
    version: int = 1
    subtitle: str = "Send emails via Sendly"
    description: str = "Perform actions on Sendly, the Tessera email service."
    defaults: Dict[str, Any] = field(default_factory=dict)
    credentials: list = field(default_factory=list)
    properties: List[NodeProperty] = field(
        default_factory=lambda: [
            NodeProperty(
                display_name="Resource",
                name="resource",
                type="options",
                options=[
                    NodePropertyOption(name="Email", value="email"),
                ],
                default="email",
                description="The resource to operate on.",
            ),
            NodeProperty(
                display_name="Operation",
                name="operation",
                type="options",
                options=[
                    NodePropertyOption(name="Send", value="send"),
                ],
                default="send",
                description="The operation to perform.",
                display_options=DisplayOptions(show={"resource": ["email"]}),
            ),
            NodeProperty(
                display_name="To",
                name="to",
                type="string",
                default="",
                required=True,
                description="Comma-separated list of recipient email addresses.",
                placeholder="user@example.com, other@example.com",
                display_options=DisplayOptions(
                    show={"resource": ["email"], "operation": ["send"]}
                ),
            ),
            NodeProperty(
                display_name="Subject",
                name="subject",
                type="string",
                default="",
                required=True,
                description="Email subject line.",
                display_options=DisplayOptions(
                    show={"resource": ["email"], "operation": ["send"]}
                ),
            ),
            NodeProperty(
                display_name="HTML",
                name="html",
                type="string",
                type_options=StringTypeOptions(editor="htmlEditor"),
                default="",
                description="HTML content of the email.",
                display_options=DisplayOptions(
                    show={"resource": ["email"], "operation": ["send"]}
                ),
            ),
            NodeProperty(
                display_name="Project ID",
                name="project_id",
                type="string",
                default="",
                required=True,
                description="The project identifier. Supports expressions, e.g. {{ event.event_data.account.id }}.",
                placeholder="{{ event.event_data.account.id }}",
                display_options=DisplayOptions(
                    show={"resource": ["email"], "operation": ["send"]}
                ),
            ),
            NodeProperty(
                display_name="From Email",
                name="from_email",
                type="string",
                default="",
                description="Sender address. Overrides the default configured in Sendly.",
                placeholder="noreply@example.com",
                display_options=DisplayOptions(
                    show={"resource": ["email"], "operation": ["send"]}
                ),
            ),
        ]
    )

    def execute(self, input: ExecutionData) -> ExecutionData:
        resource = self.parameters.get("resource", "email")
        operation = self.parameters.get("operation", "send")

        if resource == "email" and operation == "send":
            return self._send_email(input)

        input.error = f"Unknown resource/operation: {resource}/{operation}"
        return input

    def _send_email(self, input: ExecutionData) -> ExecutionData:
        from tessera_sdk.sendly.client import SendlyClient
        from tessera_sdk.sendly.schemas.create_email_request import CreateEmailRequest
        from tessera_sdk.utils.m2m_token import M2MTokenClient

        to_raw = self.get_parsed_parameter("to", input) or ""
        subject = self.get_parsed_parameter("subject", input) or ""
        html = self.get_parsed_parameter("html", input) or ""
        project_id = self.get_parsed_parameter("project_id", input) or ""
        from_email = self.get_parsed_parameter("from_email", input) or ""

        to = [addr.strip() for addr in to_raw.split(",") if addr.strip()]

        if not to:
            input.error = "At least one recipient email address is required."
            return input

        if not subject:
            input.error = "Subject is required."
            return input

        try:
            m2m_token = M2MTokenClient().get_token_sync().access_token
        except Exception as e:
            input.error = f"Sendly error (token): {str(e)}"
            return input

        try:
            client = SendlyClient(api_token=m2m_token)
            request = CreateEmailRequest(
                project_id=str(project_id) or None,
                from_email=from_email or None,
                subject=subject,
                html=html or None,
                to=to,
            )
            response = client.create_email(request)
            input.json[self.kind] = response.model_dump()
        except Exception as e:
            input.error = f"Sendly error (send): {str(e)}"

        return input


NODE = Node(
    id="orcha-nodes.sendly",
    category=CATEGORY_ACTION_APP,
    description=SendlyDescription(),
)
