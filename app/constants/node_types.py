"""Base types and dataclasses for node definitions.

These types are used by node definitions and should not have dependencies
on node implementations to avoid circular imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
class NodeResult:
    node_id: str
    node_name: str
    node_kind: str
    status: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    timestamp: str


class ExecutionContext:
    """Single source of truth for a workflow execution.

    Constructed at the start of execution and threaded through every node.
    Immutable with respect to trigger_event; append-only for node_results.
    """

    def __init__(
        self,
        trigger_event: Dict[str, Any],
        execution_id: str,
        triggered_by: str,
    ) -> None:
        self._trigger_event = trigger_event
        self._execution_id = execution_id
        self._triggered_by = triggered_by
        self._node_results: List[NodeResult] = []

    @property
    def trigger_event(self) -> Dict[str, Any]:
        return self._trigger_event

    @property
    def execution_id(self) -> str:
        return self._execution_id

    @property
    def triggered_by(self) -> str:
        return self._triggered_by

    def append_result(self, result: NodeResult) -> None:
        self._node_results.append(result)

    def get_previous_output(self) -> ExecutionData:
        """Return the output of the last executed node as ExecutionData.

        Returns empty ExecutionData if no nodes have executed yet.
        """
        if not self._node_results:
            return ExecutionData(json={})
        return ExecutionData(json=dict(self._node_results[-1].output))

    def get_node_output(self, node_name: str) -> Optional[Dict[str, Any]]:
        """Return the output of a named node, or None if not found."""
        for result in reversed(self._node_results):
            if result.node_name == node_name:
                return result.output
        return None

    def to_expression_context(self) -> Dict[str, Any]:
        """Build the dict passed to the expression engine for parameter rendering."""
        return {
            "json": self.get_previous_output().json,
            "nodes": {r.node_name: r.output for r in self._node_results},
            "execution": {
                "id": self._execution_id,
                "triggered_by": self._triggered_by,
            },
            "env": {},
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the context for persistence in WorkflowExecution.result."""
        return {
            "trigger_event": self._trigger_event,
            "node_results": [
                {
                    "node_id": r.node_id,
                    "node_name": r.node_name,
                    "node_kind": r.node_kind,
                    "status": r.status,
                    "input": r.input,
                    "output": r.output,
                    "timestamp": r.timestamp,
                }
                for r in self._node_results
            ],
        }


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
    def execute(self, context: ExecutionContext) -> ExecutionData:
        pass

    def get_parsed_parameter(
        self, parameter_name: str, context: ExecutionContext
    ) -> Any:
        """Get a parameter value parsed through the expression engine.

        Delegates to app.nodes.parameter_renderer.ParameterRenderer.
        """
        from app.nodes.parameter_renderer import ParameterRenderer

        return ParameterRenderer.for_node(self.parameters, context).get(parameter_name)

    def _process_parameter_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Recursively process a parameter value, handling expression markers.

        Delegates to app.nodes.parameter_renderer._process_value.
        """
        from app.nodes.parameter_renderer import _process_value

        return _process_value(value, context)


@dataclass
class Node:
    id: str  # e.g., "orcha-nodes.base.event_received"
    category: CategoryKey
    description: NodeDescription


__all__ = [
    "RequestConfig",
    "ExecutionData",
    "NodeResult",
    "ExecutionContext",
    "Routing",
    "PropertyField",
    "OptionItem",
    "NodeCategory",
    "NodeDescription",
    "Node",
]
