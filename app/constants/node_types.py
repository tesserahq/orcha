"""Base types and dataclasses for node definitions.

These types are used by node definitions and should not have dependencies
on node implementations to avoid circular imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.constants.node_categories import CategoryKey

if TYPE_CHECKING:
    from app.nodes.schemas.node_property import NodeProperty


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
class NodeCategory:
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
    properties: List["NodeProperty"] = field(default_factory=list)

    @abstractmethod
    def execute(self, input: ExecutionData) -> ExecutionData:
        pass


@dataclass
class Node:
    id: str  # e.g., "orcha-nodes.base.event_received"
    category: CategoryKey
    description: NodeDescription


__all__ = [
    "RequestConfig",
    "ExecutionData",
    "Routing",
    "PropertyField",
    "OptionItem",
    "NodeCategory",
    "NodeDescription",
    "Node",
]
