from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class NodeKind(BaseModel):
    """Schema representing an available node kind.

    Mirrors the structure defined in app.constants.node_kinds.
    """

    id: str
    display_name: str
    name: str
    icon: str
    group: List[str]
    version: Any  # int or list
    subtitle: Optional[str] = None
    description: str
    defaults: Dict[str, Any] = {}
    credentials: Optional[List[Dict[str, Any]]] = None
    properties: List[Dict[str, Any]] = []
    category: str


class CategoryWithNodes(BaseModel):
    """Schema representing a category with its associated node kinds."""

    key: str
    name: str
    description: str
    nodes: List[NodeKind]
