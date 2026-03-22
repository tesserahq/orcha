"""Looply node definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.constants.node_categories import CATEGORY_ACTION_APP
from app.constants.node_types import (
    ExecutionContext,
    ExecutionData,
    Node,
    NodeDescription,
)
from app.nodes.parameter_renderer import ParameterRenderer
from app.nodes.schemas.node_property import (
    DisplayOptions,
    NodeProperty,
    NodePropertyOption,
)

from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class LooplyDescription(NodeDescription):
    """Description for the Looply node."""

    display_name: str = "Looply"
    kind: str = "orcha-nodes.looply"
    icon: str = "fa:address-book"
    icon_color: str = "green"
    group: list = field(default_factory=lambda: ["action_app"])
    version: int = 1
    subtitle: str = "Manage contacts, lists, and interactions via Looply"
    description: str = (
        "Perform actions on Looply, the Tessera contact management service."
    )
    defaults: Dict[str, Any] = field(default_factory=dict)
    credentials: list = field(default_factory=list)
    properties: List[NodeProperty] = field(
        default_factory=lambda: [
            NodeProperty(
                display_name="Resource",
                name="resource",
                type="options",
                options=[
                    NodePropertyOption(name="Contact", value="contact"),
                    NodePropertyOption(name="Contact List", value="contact_list"),
                    NodePropertyOption(
                        name="Contact Interaction", value="contact_interaction"
                    ),
                    NodePropertyOption(name="Waiting List", value="waiting_list"),
                ],
                default="contact",
                description="The resource to operate on.",
            ),
            # ── Contact operations ────────────────────────────────────────────
            NodeProperty(
                display_name="Operation",
                name="operation",
                type="options",
                options=[
                    NodePropertyOption(name="Create", value="create"),
                    NodePropertyOption(name="Get", value="get"),
                    NodePropertyOption(name="Update", value="update"),
                    NodePropertyOption(name="Delete", value="delete"),
                ],
                default="create",
                description="The operation to perform.",
                display_options=DisplayOptions(show={"resource": ["contact"]}),
            ),
            NodeProperty(
                display_name="First Name",
                name="first_name",
                type="string",
                default="",
                required=True,
                description="Contact's first name.",
                display_options=DisplayOptions(
                    show={"resource": ["contact"], "operation": ["create"]}
                ),
            ),
            NodeProperty(
                display_name="Last Name",
                name="last_name",
                type="string",
                default="",
                description="Contact's last name.",
                display_options=DisplayOptions(
                    show={"resource": ["contact"], "operation": ["create", "update"]}
                ),
            ),
            NodeProperty(
                display_name="Email",
                name="email",
                type="string",
                default="",
                description="Contact's email address.",
                placeholder="contact@example.com",
                display_options=DisplayOptions(
                    show={"resource": ["contact"], "operation": ["create", "update"]}
                ),
            ),
            NodeProperty(
                display_name="Phone",
                name="phone",
                type="string",
                default="",
                description="Contact's phone number.",
                placeholder="+1-555-0123",
                display_options=DisplayOptions(
                    show={"resource": ["contact"], "operation": ["create", "update"]}
                ),
            ),
            NodeProperty(
                display_name="Company",
                name="company",
                type="string",
                default="",
                description="Contact's company.",
                display_options=DisplayOptions(
                    show={"resource": ["contact"], "operation": ["create", "update"]}
                ),
            ),
            NodeProperty(
                display_name="Contact ID",
                name="contact_id",
                type="string",
                default="",
                required=True,
                description="The UUID of the contact. Supports expressions, e.g. {{ event.event_data.contact_id }}.",
                placeholder="{{ event.event_data.contact_id }}",
                display_options=DisplayOptions(
                    show={
                        "resource": ["contact"],
                        "operation": ["get", "update", "delete"],
                    }
                ),
            ),
            # ── Contact List operations ───────────────────────────────────────
            NodeProperty(
                display_name="Operation",
                name="operation",
                type="options",
                options=[
                    NodePropertyOption(name="Create", value="create"),
                    NodePropertyOption(name="Add Members", value="add_members"),
                    NodePropertyOption(name="Remove Member", value="remove_member"),
                ],
                default="create",
                description="The operation to perform.",
                display_options=DisplayOptions(show={"resource": ["contact_list"]}),
            ),
            NodeProperty(
                display_name="List Name",
                name="list_name",
                type="string",
                default="",
                required=True,
                description="Name of the contact list.",
                display_options=DisplayOptions(
                    show={"resource": ["contact_list"], "operation": ["create"]}
                ),
            ),
            NodeProperty(
                display_name="Contact List ID",
                name="contact_list_id",
                type="string",
                default="",
                required=True,
                description="The UUID of the contact list. Supports expressions, e.g. {{ event.event_data.list_id }}.",
                placeholder="{{ event.event_data.list_id }}",
                display_options=DisplayOptions(
                    show={
                        "resource": ["contact_list"],
                        "operation": ["add_members", "remove_member"],
                    }
                ),
            ),
            NodeProperty(
                display_name="Contact IDs",
                name="contact_ids",
                type="string",
                default="",
                required=True,
                description="Comma-separated list of contact UUIDs to add.",
                placeholder="{{ event.event_data.contact_id }}",
                display_options=DisplayOptions(
                    show={"resource": ["contact_list"], "operation": ["add_members"]}
                ),
            ),
            NodeProperty(
                display_name="Contact ID",
                name="contact_id",
                type="string",
                default="",
                required=True,
                description="UUID of the contact to remove from the list.",
                placeholder="{{ event.event_data.contact_id }}",
                display_options=DisplayOptions(
                    show={"resource": ["contact_list"], "operation": ["remove_member"]}
                ),
            ),
            # ── Contact Interaction operations ────────────────────────────────
            NodeProperty(
                display_name="Operation",
                name="operation",
                type="options",
                options=[
                    NodePropertyOption(name="Create", value="create"),
                ],
                default="create",
                description="The operation to perform.",
                display_options=DisplayOptions(
                    show={"resource": ["contact_interaction"]}
                ),
            ),
            NodeProperty(
                display_name="Contact ID",
                name="contact_id",
                type="string",
                default="",
                required=True,
                description="UUID of the contact for this interaction. Supports expressions.",
                placeholder="{{ event.event_data.contact_id }}",
                display_options=DisplayOptions(
                    show={"resource": ["contact_interaction"], "operation": ["create"]}
                ),
            ),
            NodeProperty(
                display_name="Note",
                name="note",
                type="string",
                default="",
                description="Notes about the interaction.",
                display_options=DisplayOptions(
                    show={"resource": ["contact_interaction"], "operation": ["create"]}
                ),
            ),
            NodeProperty(
                display_name="Action",
                name="action",
                type="string",
                default="",
                description="Follow-up action (e.g. 'Follow up in 2 weeks').",
                display_options=DisplayOptions(
                    show={"resource": ["contact_interaction"], "operation": ["create"]}
                ),
            ),
            # ── Waiting List operations ───────────────────────────────────────
            NodeProperty(
                display_name="Operation",
                name="operation",
                type="options",
                options=[
                    NodePropertyOption(name="Add Members", value="add_members"),
                    NodePropertyOption(
                        name="Update Member Status", value="update_member_status"
                    ),
                ],
                default="add_members",
                description="The operation to perform.",
                display_options=DisplayOptions(show={"resource": ["waiting_list"]}),
            ),
            NodeProperty(
                display_name="Waiting List ID",
                name="waiting_list_id",
                type="string",
                default="",
                required=True,
                description="The UUID of the waiting list. Supports expressions.",
                placeholder="{{ event.event_data.waiting_list_id }}",
                display_options=DisplayOptions(
                    show={
                        "resource": ["waiting_list"],
                        "operation": ["add_members", "update_member_status"],
                    }
                ),
            ),
            NodeProperty(
                display_name="Contact IDs",
                name="contact_ids",
                type="string",
                default="",
                required=True,
                description="Comma-separated list of contact UUIDs to add.",
                placeholder="{{ event.event_data.contact_id }}",
                display_options=DisplayOptions(
                    show={"resource": ["waiting_list"], "operation": ["add_members"]}
                ),
            ),
            NodeProperty(
                display_name="Contact ID",
                name="contact_id",
                type="string",
                default="",
                required=True,
                description="UUID of the contact whose status to update.",
                placeholder="{{ event.event_data.contact_id }}",
                display_options=DisplayOptions(
                    show={
                        "resource": ["waiting_list"],
                        "operation": ["update_member_status"],
                    }
                ),
            ),
            NodeProperty(
                display_name="Status",
                name="status",
                type="options",
                options=[
                    NodePropertyOption(name="Pending", value="pending"),
                    NodePropertyOption(name="Approved", value="approved"),
                    NodePropertyOption(name="Rejected", value="rejected"),
                    NodePropertyOption(name="Notified", value="notified"),
                    NodePropertyOption(name="Accepted", value="accepted"),
                    NodePropertyOption(name="Declined", value="declined"),
                    NodePropertyOption(name="Active", value="active"),
                    NodePropertyOption(name="Inactive", value="inactive"),
                    NodePropertyOption(name="Cancelled", value="cancelled"),
                ],
                default="pending",
                required=True,
                description="New status for the waiting list member.",
                display_options=DisplayOptions(
                    show={
                        "resource": ["waiting_list"],
                        "operation": ["update_member_status"],
                    }
                ),
            ),
        ]
    )

    def execute(self, context: ExecutionContext) -> ExecutionData:
        resource = self.parameters.get("resource", "contact")
        operation = self.parameters.get("operation", "create")

        if resource == "contact":
            if operation == "create":
                return self._create_contact(context)
            if operation == "get":
                return self._get_contact(context)
            if operation == "update":
                return self._update_contact(context)
            if operation == "delete":
                return self._delete_contact(context)

        if resource == "contact_list":
            if operation == "create":
                return self._create_contact_list(context)
            if operation == "add_members":
                return self._add_members_to_contact_list(context)
            if operation == "remove_member":
                return self._remove_member_from_contact_list(context)

        if resource == "contact_interaction":
            if operation == "create":
                return self._create_contact_interaction(context)

        if resource == "waiting_list":
            if operation == "add_members":
                return self._add_members_to_waiting_list(context)
            if operation == "update_member_status":
                return self._update_waiting_list_member_status(context)

        output = context.get_previous_output()
        output.error = f"Unknown resource/operation: {resource}/{operation}"
        return output

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_client(self, output: ExecutionData) -> Optional[Any]:
        """Acquire an M2M token and return an authenticated LooplyClient, or set output.error."""
        from tessera_sdk.clients.looply import LooplyClient
        from tessera_sdk.infra.m2m_token import M2MTokenClient

        try:
            m2m_token = M2MTokenClient().get_token_sync().access_token
        except Exception as e:
            output.error = f"Looply error (token): {str(e)}"
            return None
        return LooplyClient(api_token=m2m_token)

    # ── Contact operations ────────────────────────────────────────────────────

    def _create_contact(self, context: ExecutionContext) -> ExecutionData:
        from tessera_sdk.clients.looply.schemas.contact import ContactCreateRequest

        p = ParameterRenderer.for_node(self.parameters, context)
        first_name = p.get("first_name") or ""
        last_name = p.get("last_name") or ""
        email = p.get("email") or ""
        phone = p.get("phone") or ""
        company = p.get("company") or ""

        output = context.get_previous_output()

        if not first_name:
            output.error = "First name is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            request = ContactCreateRequest(
                first_name=first_name,
                last_name=last_name or None,
                email=email or None,
                phone=phone or None,
                company=company or None,
            )
            response = client.create_contact(request)
            output.json[self.kind] = response.model_dump(mode="json")
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (create contact): {str(e)}"

        return output

    def _get_contact(self, context: ExecutionContext) -> ExecutionData:
        p = ParameterRenderer.for_node(self.parameters, context)
        contact_id = p.get("contact_id") or ""

        output = context.get_previous_output()

        if not contact_id:
            output.error = "Contact ID is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            response = client.get_contact(contact_id)
            output.json[self.kind] = response.model_dump(mode="json")
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (get contact): {str(e)}"

        return output

    def _update_contact(self, context: ExecutionContext) -> ExecutionData:
        from tessera_sdk.clients.looply.schemas.contact import ContactUpdate

        p = ParameterRenderer.for_node(self.parameters, context)
        contact_id = p.get("contact_id") or ""
        last_name = p.get("last_name") or ""
        email = p.get("email") or ""
        phone = p.get("phone") or ""
        company = p.get("company") or ""

        output = context.get_previous_output()

        if not contact_id:
            output.error = "Contact ID is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            request = ContactUpdate(
                last_name=last_name or None,
                email=email or None,
                phone=phone or None,
                company=company or None,
            )
            response = client.update_contact(contact_id, request)
            output.json[self.kind] = response.model_dump(mode="json")
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (update contact): {str(e)}"

        return output

    def _delete_contact(self, context: ExecutionContext) -> ExecutionData:
        p = ParameterRenderer.for_node(self.parameters, context)
        contact_id = p.get("contact_id") or ""

        output = context.get_previous_output()

        if not contact_id:
            output.error = "Contact ID is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            client.delete_contact(contact_id)
            output.json[self.kind] = {"deleted": True, "contact_id": contact_id}
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (delete contact): {str(e)}"

        return output

    # ── Contact List operations ───────────────────────────────────────────────

    def _create_contact_list(self, context: ExecutionContext) -> ExecutionData:
        from tessera_sdk.clients.looply.schemas.contact_list import (
            ContactListCreateRequest,
        )

        p = ParameterRenderer.for_node(self.parameters, context)
        list_name = p.get("list_name") or ""

        output = context.get_previous_output()

        if not list_name:
            output.error = "List name is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            request = ContactListCreateRequest(name=list_name)
            response = client.create_contact_list(request)
            output.json[self.kind] = response.model_dump(mode="json")
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (create contact list): {str(e)}"

        return output

    def _add_members_to_contact_list(self, context: ExecutionContext) -> ExecutionData:
        from tessera_sdk.clients.looply.schemas.contact_list import AddMembersRequest

        p = ParameterRenderer.for_node(self.parameters, context)
        contact_list_id = p.get("contact_list_id") or ""
        contact_ids_raw = p.get("contact_ids") or ""

        output = context.get_previous_output()

        if not contact_list_id:
            output.error = "Contact List ID is required."
            return output

        contact_ids = [cid.strip() for cid in contact_ids_raw.split(",") if cid.strip()]
        if not contact_ids:
            output.error = "At least one contact ID is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            request = AddMembersRequest(contact_ids=contact_ids)
            response = client.add_members_to_contact_list(contact_list_id, request)
            output.json[self.kind] = response
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (add members to contact list): {str(e)}"

        return output

    def _remove_member_from_contact_list(
        self, context: ExecutionContext
    ) -> ExecutionData:
        p = ParameterRenderer.for_node(self.parameters, context)
        contact_list_id = p.get("contact_list_id") or ""
        contact_id = p.get("contact_id") or ""

        output = context.get_previous_output()

        if not contact_list_id:
            output.error = "Contact List ID is required."
            return output

        if not contact_id:
            output.error = "Contact ID is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            client.remove_member_from_contact_list(contact_list_id, contact_id)
            output.json[self.kind] = {
                "removed": True,
                "contact_list_id": contact_list_id,
                "contact_id": contact_id,
            }
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (remove member from contact list): {str(e)}"

        return output

    # ── Contact Interaction operations ────────────────────────────────────────

    def _create_contact_interaction(self, context: ExecutionContext) -> ExecutionData:
        from tessera_sdk.clients.looply.schemas.contact_interaction import (
            ContactInteractionCreateRequest,
        )

        p = ParameterRenderer.for_node(self.parameters, context)
        contact_id = p.get("contact_id") or ""
        note = p.get("note") or ""
        action = p.get("action") or ""

        output = context.get_previous_output()

        if not contact_id:
            output.error = "Contact ID is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            request = ContactInteractionCreateRequest(
                note=note or None,
                action=action or None,
            )
            response = client.create_contact_interaction(contact_id, request)
            output.json[self.kind] = response.model_dump(mode="json")
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (create interaction): {str(e)}"

        return output

    # ── Waiting List operations ───────────────────────────────────────────────

    def _add_members_to_waiting_list(self, context: ExecutionContext) -> ExecutionData:
        from tessera_sdk.clients.looply.schemas.waiting_list import (
            AddWaitingListMembersRequest,
        )

        p = ParameterRenderer.for_node(self.parameters, context)
        waiting_list_id = p.get("waiting_list_id") or ""
        contact_ids_raw = p.get("contact_ids") or ""

        output = context.get_previous_output()

        if not waiting_list_id:
            output.error = "Waiting List ID is required."
            return output

        contact_ids = [cid.strip() for cid in contact_ids_raw.split(",") if cid.strip()]
        if not contact_ids:
            output.error = "At least one contact ID is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            request = AddWaitingListMembersRequest(contact_ids=contact_ids)
            response = client.add_members_to_waiting_list(waiting_list_id, request)
            output.json[self.kind] = response
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (add members to waiting list): {str(e)}"

        return output

    def _update_waiting_list_member_status(
        self, context: ExecutionContext
    ) -> ExecutionData:
        p = ParameterRenderer.for_node(self.parameters, context)
        waiting_list_id = p.get("waiting_list_id") or ""
        contact_id = p.get("contact_id") or ""
        status = p.get("status") or ""

        output = context.get_previous_output()

        if not waiting_list_id:
            output.error = "Waiting List ID is required."
            return output

        if not contact_id:
            output.error = "Contact ID is required."
            return output

        if not status:
            output.error = "Status is required."
            return output

        client = self._get_client(output)
        if client is None:
            return output

        try:
            response = client.update_waiting_list_member_status(
                waiting_list_id, contact_id, status
            )
            output.json[self.kind] = response
        except Exception as e:
            logger.exception(e)
            output.error = f"Looply error (update waiting list member status): {str(e)}"

        return output


NODE = Node(
    id="orcha-nodes.looply",
    category=CATEGORY_ACTION_APP,
    description=LooplyDescription(),
)
