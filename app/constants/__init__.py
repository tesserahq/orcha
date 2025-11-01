"""Constants package for the application."""

from app.constants.node_categories import (
    CategoryKey,
    NodeCategory,
    Node,
    NodeDescription,
    NodeKindDict,
    PropertyField,
    OptionItem,
    RequestConfig,
    Routing,
    CATEGORY_TRIGGER,
    CATEGORY_CORE,
    CATEGORY_FLOW,
    CATEGORY_DATA_TRANSFORMATION,
    CATEGORY_ACTION_APP,
    NODE_CATEGORIES,
    NODE_KINDS,
    NODE_KIND_BY_ID,
    NODE_KINDS_BY_CATEGORY,
    NODE_BY_ID,
)

# Type alias for backward compatibility or convenience
NodeType = CategoryKey

__all__ = [
    "CategoryKey",
    "NodeType",
    "NodeCategory",
    "Node",
    "NodeDescription",
    "NodeKindDict",
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
