"""Node categories and kinds used across the application.

Provides a typed, centralized registry of node categories and kinds so that
APIs, UI, and validations can remain consistent.
"""

from __future__ import annotations

from typing import Dict, List, Literal, TypedDict


# Category keys are stable identifiers suitable for storage and lookups
# Expose them as constants to avoid string literals throughout the codebase.
CATEGORY_TRIGGER = "trigger"
CATEGORY_CORE = "core"
CATEGORY_FLOW = "flow"
CATEGORY_DATA_TRANSFORMATION = "data_transformation"

CategoryKey = Literal["trigger", "core", "flow", "data_transformation"]


class NodeCategory(TypedDict):
    key: CategoryKey
    name: str
    description: str


class NodeKind(TypedDict):
    id: str  # e.g., "orcha-nodes.base.event_received"
    name: str
    description: str
    category: CategoryKey


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
}


# Kind registry
NODE_KINDS: List[NodeKind] = [
    # Trigger
    {
        "id": "orcha-nodes.base.event_received",
        "name": "Event Received",
        "description": "Trigger a workflow when a matching event is received.",
        "category": CATEGORY_TRIGGER,
    },
    # Core
    {
        "id": "orcha-nodes.base.http_request",
        "name": "HttpRequest",
        "description": "Makes an http request and returns the response data.",
        "category": CATEGORY_CORE,
    },
    # Flow
    {
        "id": "orcha-nodes.base.filter",
        "name": "Filter",
        "description": "Remove items matching a condition.",
        "category": CATEGORY_FLOW,
    },
    {
        "id": "orcha-nodes.base.if",
        "name": "If",
        "description": "Route items to different branches (true/false).",
        "category": CATEGORY_FLOW,
    },
    # Data Transformation
    {
        "id": "orcha-nodes.base.date_time",
        "name": "Date & Time",
        "description": "Manipulate date and time values.",
        "category": CATEGORY_DATA_TRANSFORMATION,
    },
    {
        "id": "orcha-nodes.base.edit_fields",
        "name": "Edit Fields",
        "description": "Modify, add, or remove item fields.",
        "category": CATEGORY_DATA_TRANSFORMATION,
    },
]


# Fast lookups by id or category
NODE_KIND_BY_ID: Dict[str, NodeKind] = {kind["id"]: kind for kind in NODE_KINDS}

NODE_KINDS_BY_CATEGORY: Dict[CategoryKey, List[NodeKind]] = {
    key: [k for k in NODE_KINDS if k["category"] == key] for key in NODE_CATEGORIES
}


__all__ = [
    "CategoryKey",
    "NodeCategory",
    "NodeKind",
    "CATEGORY_TRIGGER",
    "CATEGORY_CORE",
    "CATEGORY_FLOW",
    "CATEGORY_DATA_TRANSFORMATION",
    "NODE_CATEGORIES",
    "NODE_KINDS",
    "NODE_KIND_BY_ID",
    "NODE_KINDS_BY_CATEGORY",
]
