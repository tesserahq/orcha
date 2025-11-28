"""Base types and dataclasses for node definitions.

These types are used by node definitions and should not have dependencies
on node implementations to avoid circular imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from app.constants.node_categories import CategoryKey
from app.schemas.event import EventBase as EventSchema
from tessera_sdk.utils.expressions.engine import ExpressionEngine

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
    event: Optional[EventSchema] = None

    def has_event(self) -> bool:
        return self.event is not None


@dataclass
class Routing:
    request: RequestConfig


@dataclass
class PropertyField:
    display_name: str
    name: str
    type: str
    default: Any = None
    required: bool = False
    description: Optional[str] = None
    options: Optional[List[OptionItem]] = None
    display_options: Optional[Dict[str, Any]] = None


@dataclass
class OptionItem:
    name: str
    value: Any
    description: Optional[str] = None
    action: Optional[str] = None
    routing: Optional[Routing] = None
    display_options: Optional[Dict[str, Any]] = None


@dataclass
class NodeCategory:
    key: CategoryKey
    name: str
    description: str


@dataclass
class NodeDescription(ABC):
    display_name: str
    kind: str
    icon: str
    icon_color: str
    group: List[str]
    version: Any  # int or list
    subtitle: Optional[str]
    description: str
    defaults: Dict[str, Any]
    credentials: Optional[List[Dict[str, Any]]] = None
    properties: List["NodeProperty"] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def execute(self, input: ExecutionData) -> ExecutionData:
        pass

    def get_parsed_parameter(
        self, parameter_name: str, input_data: ExecutionData
    ) -> Any:
        """
        Get a parameter value parsed through the expression engine.

        This method retrieves a parameter from self.parameters and if it's a string,
        parses it through the ExpressionEngine using the input data context.

        Args:
            parameter_name: The name of the parameter to retrieve
            input_data: The ExecutionData containing json, node outputs, etc.

        Returns:
            The parsed parameter value. If the parameter is a string, it will be
            rendered through the expression engine. Non-string values are returned as-is.
        """
        # Get the raw parameter value
        raw_value = self.parameters.get(parameter_name)

        # If it's not a string, return as-is
        if not isinstance(raw_value, str):
            return raw_value

        # Build context for expression engine
        # json: current execution data
        context: Dict[str, Any] = {
            "json": input_data.json,
            "event": input_data.event.model_dump() if input_data.event else {},
            # env: environment variables (empty dict for now, can be extended)
            "env": {},
        }

        # Use expression engine to render the template
        engine = ExpressionEngine()
        return engine.render(raw_value, context)


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
