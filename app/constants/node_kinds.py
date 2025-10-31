"""Node categories and kinds used across the application.

Provides a typed, centralized registry of node categories and kinds so that
APIs, UI, and validations can remain consistent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, TypedDict
from abc import ABC, abstractmethod


# Category keys are stable identifiers suitable for storage and lookups
# Expose them as constants to avoid string literals throughout the codebase.
CATEGORY_TRIGGER = "trigger"
CATEGORY_CORE = "core"
CATEGORY_FLOW = "flow"
CATEGORY_DATA_TRANSFORMATION = "data_transformation"
CATEGORY_ACTION_APP = "action_app"

CategoryKey = Literal["trigger", "core", "flow", "data_transformation", "action_app"]


@dataclass
class RequestConfig:
    method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    qs: Optional[Dict[str, Any]] = None  # query string parameters.
    body: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionData:
    json: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class Routing:
    request: RequestConfig


@dataclass
class PropertyField:
    displayName: str
    name: str
    type: str
    default: Any = None
    required: bool = False
    description: Optional[str] = None
    options: Optional[List[OptionItem]] = None
    displayOptions: Optional[Dict[str, Any]] = None


@dataclass
class OptionItem:
    name: str
    value: Any
    description: Optional[str] = None
    action: Optional[str] = None
    routing: Optional[Routing] = None
    displayOptions: Optional[Dict[str, Any]] = None


@dataclass
class NodeCategory(TypedDict):
    key: CategoryKey
    name: str
    description: str


@dataclass
class NodeDescription(ABC):
    displayName: str
    name: str
    icon: str
    group: List[str]
    version: Any  # int or list
    subtitle: Optional[str]
    description: str
    defaults: Dict[str, Any]
    inputs: List[str]
    outputs: List[str]
    credentials: Optional[List[Dict[str, Any]]] = None
    requestDefaults: Optional[RequestConfig] = None
    properties: List[PropertyField] = field(default_factory=list)

    @abstractmethod
    def execute(self, input: ExecutionData) -> ExecutionData:
        pass


@dataclass
class Node:
    id: str  # e.g., "orcha-nodes.base.event_received"
    category: CategoryKey
    description: NodeDescription


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


# Import all node definitions from the nodes folder
from app.nodes import (
    EVENT_RECEIVED_NODE,
    HTTP_REQUEST_NODE,
    FILTER_NODE,
    IF_NODE,
    DATE_TIME_NODE,
    EDIT_FIELDS_NODE,
)

# All node instances
_ALL_NODES: List[Node] = [
    EVENT_RECEIVED_NODE,
    HTTP_REQUEST_NODE,
    FILTER_NODE,
    IF_NODE,
    DATE_TIME_NODE,
    EDIT_FIELDS_NODE,
]


class NodeKindDictRequired(TypedDict):
    """Required fields for NodeKindDict."""

    id: str
    displayName: str
    name: str
    icon: str
    group: List[str]
    version: Any  # int or list
    description: str
    defaults: Dict[str, Any]
    inputs: List[str]
    outputs: List[str]
    properties: List[Dict[str, Any]]
    category: str


class NodeKindDict(NodeKindDictRequired, total=False):
    """Node kind dictionary format for API responses."""

    subtitle: Optional[str]
    credentials: Optional[List[Dict[str, Any]]]
    requestDefaults: Optional[Dict[str, Any]]


def _serialize_property_field(prop: PropertyField) -> Dict[str, Any]:
    """Serialize a PropertyField to a dictionary."""
    result: Dict[str, Any] = {
        "displayName": prop.displayName,
        "name": prop.name,
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
                    {"displayOptions": opt.displayOptions} if opt.displayOptions else {}
                ),
            }
            for opt in prop.options
        ]
    if prop.displayOptions:
        result["displayOptions"] = prop.displayOptions
    return result


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


def _node_to_kind_dict(node: Node) -> NodeKindDict:
    """Convert a Node instance to the API format."""
    desc = node.description
    result: NodeKindDict = {
        "id": node.id,
        "displayName": desc.displayName,
        "name": desc.name,
        "icon": desc.icon,
        "group": desc.group,
        "version": desc.version,
        "description": desc.description,
        "defaults": desc.defaults,
        "inputs": desc.inputs,
        "outputs": desc.outputs,
        "properties": [_serialize_property_field(prop) for prop in desc.properties],
        "category": node.category,
    }

    if desc.subtitle is not None:
        result["subtitle"] = desc.subtitle
    if desc.credentials is not None:
        result["credentials"] = desc.credentials
    if desc.requestDefaults is not None:
        result["requestDefaults"] = _serialize_request_config(desc.requestDefaults)

    return result


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
    "CategoryKey",
    "NodeCategory",
    "NodeKindDict",
    "Node",
    "NodeDescription",
    "PropertyField",
    "OptionItem",
    "RequestConfig",
    "Routing",
    "CATEGORY_TRIGGER",
    "CATEGORY_CORE",
    "CATEGORY_FLOW",
    "CATEGORY_DATA_TRANSFORMATION",
    "CATEGORY_ACTION_APP",
    "NODE_CATEGORIES",
    "NODE_KINDS",
    "NODE_KIND_BY_ID",
    "NODE_KINDS_BY_CATEGORY",
    "NODE_BY_ID",
]
