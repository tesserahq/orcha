"""Node categories and kinds used across the application.

Provides a typed, centralized registry of node categories and kinds so that
APIs, UI, and validations can remain consistent.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from app.nodes.schemas.node_property import NodeProperty

from app.constants.node_categories import (
    CATEGORY_TRIGGER,
    CATEGORY_CORE,
    CATEGORY_FLOW,
    CATEGORY_DATA_TRANSFORMATION,
    CATEGORY_ACTION_APP,
    CategoryKey,
)
from app.constants.node_types import (
    Node,
    NodeCategory,
    NodeDescription,
    OptionItem,
    PropertyField,
    RequestConfig,
    Routing,
)


# Category registry
NODE_CATEGORIES: Dict[CategoryKey, NodeCategory] = {
    CATEGORY_TRIGGER: {
        "key": CATEGORY_TRIGGER,
        "name": "Trigger",
        "description": (
            "Triggers start your workflow. Workflows can have multiple triggers."
        ),
    },
    CATEGORY_CORE: {
        "key": CATEGORY_CORE,
        "name": "Core",
        "description": "Run code, make http requests, set webhooks, etc.",
    },
    CATEGORY_FLOW: {
        "key": CATEGORY_FLOW,
        "name": "Flow",
        "description": "Branch, merge or loop the flow, etc.",
    },
    CATEGORY_DATA_TRANSFORMATION: {
        "key": CATEGORY_DATA_TRANSFORMATION,
        "name": "Data Transformation",
        "description": "Manipulate, filter or convert data.",
    },
    CATEGORY_ACTION_APP: {
        "key": CATEGORY_ACTION_APP,
        "name": "Action in an app",
        "description": (
            "Do something in an app or service like Looply, Identies, Slack"
        ),
    },
}


# All node instances - imported at the bottom to avoid circular imports
_ALL_NODES: List[Node] = []


class NodeKindDictRequired(TypedDict):
    """Required fields for NodeKindDict."""

    id: str
    display_name: str
    name: str
    icon: str
    group: List[str]
    version: Any  # int or list
    description: str
    defaults: Dict[str, Any]
    properties: List[Dict[str, Any]]
    category: str


class NodeKindDict(NodeKindDictRequired, total=False):
    """Node kind dictionary format for API responses."""

    subtitle: Optional[str]
    credentials: Optional[List[Dict[str, Any]]]


def _serialize_property_field(prop: PropertyField) -> Dict[str, Any]:
    """Serialize a PropertyField to a dictionary."""
    result: Dict[str, Any] = {
        "display_name": prop.display_name,
        "kind": prop.kind,
        "type": prop.type,
        "required": prop.required,
    }
    if prop.default is not None:
        result["default"] = prop.default
    if prop.description:
        result["description"] = prop.description
    if prop.options:
        result["options"] = [
            {
                "name": opt.name,
                "value": opt.value,
                **({"description": opt.description} if opt.description else {}),
                **({"action": opt.action} if opt.action else {}),
                **(
                    {
                        "routing": (
                            _serialize_routing(opt.routing) if opt.routing else None
                        )
                    }
                    if opt.routing
                    else {}
                ),
                **(
                    {"display_options": opt.display_options}
                    if opt.display_options
                    else {}
                ),
            }
            for opt in prop.options
        ]
    if prop.display_options:
        result["display_options"] = prop.display_options
    return result


def _serialize_node_property(prop: "NodeProperty") -> Dict[str, Any]:
    """Serialize a NodeProperty (Pydantic model) to a dictionary."""

    result: Dict[str, Any] = {
        "display_name": prop.display_name,
        "name": prop.name,
        "type": prop.type,
    }

    if prop.default is not None:
        result["default"] = prop.default
    if prop.description:
        result["description"] = prop.description
    if prop.hint:
        result["hint"] = prop.hint
    if prop.placeholder:
        result["placeholder"] = prop.placeholder
    if prop.required is not None:
        result["required"] = prop.required
    if prop.type_options:
        # Serialize type_options to camelCase
        type_opts = prop.type_options
        type_options_dict: Dict[str, Any] = {}

        # Handle all possible type options fields
        if hasattr(type_opts, "multiple_values") and type_opts.multiple_values:
            type_options_dict["multipleValues"] = type_opts.multiple_values
        if (
            hasattr(type_opts, "multiple_value_button_text")
            and type_opts.multiple_value_button_text
        ):
            type_options_dict["multipleValueButtonText"] = (
                type_opts.multiple_value_button_text
            )
        if hasattr(type_opts, "sortable") and type_opts.sortable is not None:
            type_options_dict["sortable"] = type_opts.sortable
        if hasattr(type_opts, "password") and type_opts.password:
            type_options_dict["password"] = type_opts.password
        if hasattr(type_opts, "rows") and type_opts.rows is not None:
            type_options_dict["rows"] = type_opts.rows
        if hasattr(type_opts, "code_autocomplete") and type_opts.code_autocomplete:
            type_options_dict["codeAutocomplete"] = type_opts.code_autocomplete
        if hasattr(type_opts, "editor") and type_opts.editor:
            type_options_dict["editor"] = type_opts.editor
        if (
            hasattr(type_opts, "editor_is_read_only")
            and type_opts.editor_is_read_only is not None
        ):
            type_options_dict["editorIsReadOnly"] = type_opts.editor_is_read_only
        if hasattr(type_opts, "sql_dialect") and type_opts.sql_dialect:
            type_options_dict["sqlDialect"] = type_opts.sql_dialect
        if hasattr(type_opts, "min_value") and type_opts.min_value is not None:
            type_options_dict["minValue"] = type_opts.min_value
        if hasattr(type_opts, "max_value") and type_opts.max_value is not None:
            type_options_dict["maxValue"] = type_opts.max_value
        if (
            hasattr(type_opts, "number_precision")
            and type_opts.number_precision is not None
        ):
            type_options_dict["numberPrecision"] = type_opts.number_precision
        if hasattr(type_opts, "load_options_method") and type_opts.load_options_method:
            type_options_dict["loadOptionsMethod"] = type_opts.load_options_method
        if (
            hasattr(type_opts, "load_options_depends_on")
            and type_opts.load_options_depends_on
        ):
            type_options_dict["loadOptionsDependsOn"] = (
                type_opts.load_options_depends_on
            )
        if hasattr(type_opts, "load_options") and type_opts.load_options:
            type_options_dict["loadOptions"] = type_opts.load_options
        if (
            hasattr(type_opts, "allow_arbitrary_values")
            and type_opts.allow_arbitrary_values is not None
        ):
            type_options_dict["allowArbitraryValues"] = type_opts.allow_arbitrary_values
        if (
            hasattr(type_opts, "min_required_fields")
            and type_opts.min_required_fields is not None
        ):
            type_options_dict["minRequiredFields"] = type_opts.min_required_fields
        if (
            hasattr(type_opts, "max_allowed_fields")
            and type_opts.max_allowed_fields is not None
        ):
            type_options_dict["maxAllowedFields"] = type_opts.max_allowed_fields
        if (
            hasattr(type_opts, "always_open_edit_window")
            and type_opts.always_open_edit_window is not None
        ):
            type_options_dict["alwaysOpenEditWindow"] = (
                type_opts.always_open_edit_window
            )
        if hasattr(type_opts, "show_alpha") and type_opts.show_alpha is not None:
            type_options_dict["showAlpha"] = type_opts.show_alpha
        if hasattr(type_opts, "expirable") and type_opts.expirable is not None:
            type_options_dict["expirable"] = type_opts.expirable
        if hasattr(type_opts, "container_class") and type_opts.container_class:
            type_options_dict["containerClass"] = type_opts.container_class

        if type_options_dict:
            result["typeOptions"] = type_options_dict

    if prop.display_options:
        display_opts: Dict[str, Any] = {}
        if prop.display_options.show:
            display_opts["show"] = prop.display_options.show
        if prop.display_options.hide:
            display_opts["hide"] = prop.display_options.hide
        if display_opts:
            result["display_options"] = display_opts

    if prop.disabled_options:
        disabled_opts: Dict[str, Any] = {}
        if prop.disabled_options.show:
            disabled_opts["show"] = prop.disabled_options.show
        if prop.disabled_options.hide:
            disabled_opts["hide"] = prop.disabled_options.hide
        if disabled_opts:
            result["disabledOptions"] = disabled_opts

    if prop.options:
        result["options"] = [_serialize_property_option(opt) for opt in prop.options]

    if prop.credential_types:
        result["credentialTypes"] = prop.credential_types

    return result


def _serialize_property_option(opt: Any) -> Dict[str, Any]:
    """Serialize a property option (NodePropertyOption, NodeProperty, or NodePropertyCollection)."""
    from app.nodes.schemas.node_property import (
        NodePropertyOption,
        NodePropertyCollection,
    )

    if isinstance(opt, NodePropertyOption):
        result: Dict[str, Any] = {
            "name": opt.name,
            "value": opt.value,
        }
        if opt.description:
            result["description"] = opt.description
        return result
    elif isinstance(opt, NodePropertyCollection):
        result = {
            "display_name": opt.display_name,
            "name": opt.name,
            "values": [_serialize_node_property(val) for val in opt.values],
        }
        return result
    else:
        # It's a NodeProperty (recursive)
        return _serialize_node_property(opt)


def _serialize_routing(routing: Routing) -> Dict[str, Any]:
    """Serialize a Routing to a dictionary."""
    return {"request": _serialize_request_config(routing.request)}


def _serialize_request_config(request: RequestConfig) -> Dict[str, Any]:
    """Serialize a RequestConfig to a dictionary."""
    result: Dict[str, Any] = {
        "method": request.method,
        "url": request.url,
    }
    if request.headers:
        result["headers"] = request.headers
    if request.qs:
        result["qs"] = request.qs
    if request.body:
        result["body"] = request.body
    return result


def _kind_to_name(kind: str) -> str:
    """Convert a node kind to a camelCase name.

    Example: "orcha-nodes.base.date_time" -> "dateTime"
    """
    # Extract the last part after the last dot
    return kind.split(".")[-1]


def _node_to_kind_dict(node: Node) -> NodeKindDict:
    """Convert a Node instance to the API format."""
    desc = node.description
    result: NodeKindDict = {
        "id": node.id,
        "display_name": desc.display_name,
        "name": _kind_to_name(desc.kind),
        "icon": desc.icon,
        "group": desc.group,
        "version": desc.version,
        "description": desc.description,
        "defaults": desc.defaults,
        "properties": [_serialize_node_property(prop) for prop in desc.properties],
        "category": node.category,
    }

    if desc.subtitle is not None:
        result["subtitle"] = desc.subtitle
    if desc.credentials is not None:
        result["credentials"] = desc.credentials

    return result


# Import all node definitions from the nodes folder
# This is done at the bottom to avoid circular imports
from app.nodes import (
    EVENT_RECEIVED_NODE,
    HTTP_REQUEST_NODE,
    FILTER_NODE,
    IF_NODE,
    DATE_TIME_NODE,
    EDIT_FIELDS_NODE,
    TEST_ACTION_NODE,
)

# All node instances
_ALL_NODES = [
    EVENT_RECEIVED_NODE,
    HTTP_REQUEST_NODE,
    FILTER_NODE,
    IF_NODE,
    DATE_TIME_NODE,
    EDIT_FIELDS_NODE,
    TEST_ACTION_NODE,
]

# Kind registry - converted to dict format for API compatibility
NODE_KINDS: List[NodeKindDict] = [_node_to_kind_dict(node) for node in _ALL_NODES]

# Fast lookups by id or category
NODE_KIND_BY_ID: Dict[str, NodeKindDict] = {kind["id"]: kind for kind in NODE_KINDS}

NODE_KINDS_BY_CATEGORY: Dict[CategoryKey, List[NodeKindDict]] = {
    key: [k for k in NODE_KINDS if k["category"] == key] for key in NODE_CATEGORIES
}

# Lookup original Node instances by id
NODE_BY_ID: Dict[str, Node] = {node.id: node for node in _ALL_NODES}


__all__ = [
    "NodeCategory",
    "NodeKindDict",
    "Node",
    "NodeDescription",
    "PropertyField",
    "OptionItem",
    "RequestConfig",
    "Routing",
    "NODE_CATEGORIES",
    "NODE_KINDS",
    "NODE_KIND_BY_ID",
    "NODE_KINDS_BY_CATEGORY",
    "NODE_BY_ID",
]
