"""Base types and dataclasses for node definitions.

These types are used by node definitions and should not have dependencies
on node implementations to avoid circular imports.
"""

from __future__ import annotations

import ast
import json
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

        This method retrieves a parameter from self.parameters and if it's a string or dict,
        parses it through the ExpressionEngine using the input data context.

        Supports two modes:
        1. String templates: "{{ event.event_data.account }}" → renders as string
        2. Expression objects: {"__expr__": "{{ event.event_data.account }}"} → evaluates
           expression and returns the result as a Python object (dict, list, etc.)

        Args:
            parameter_name: The name of the parameter to retrieve
            input_data: The ExecutionData containing json, node outputs, etc.

        Returns:
            The parsed parameter value. If the parameter is a string or dict, it will be
            rendered through the expression engine. Other non-string values are returned as-is.
        """
        # Get the raw parameter value
        raw_value = self.parameters.get(parameter_name)

        # Build context for expression engine
        context: Dict[str, Any] = {
            "json": input_data.json,
            "event": input_data.event.model_dump() if input_data.event else {},
            # env: environment variables (empty dict for now, can be extended)
            "env": {},
        }

        # Recursively process the value to handle nested expression markers
        # This must be called with the original value (not JSON string) to detect __expr__ markers
        return self._process_parameter_value(raw_value, context)

    def _process_parameter_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """
        Recursively process a parameter value, handling expression markers.

        Args:
            value: The value to process (can be dict, list, string, or other)
            context: The context for expression evaluation

        Returns:
            The processed value with expressions evaluated
        """
        # Check if this is an expression marker object
        if isinstance(value, dict) and "__expr__" in value:
            # This is an expression that should evaluate to an object (not a string)
            expr_str = value["__expr__"]
            if not isinstance(expr_str, str):
                return value

            # Evaluate the expression directly using Jinja2
            engine = ExpressionEngine()
            template = engine.env.from_string(expr_str)

            # Render the template - Jinja2 always returns a string, so we need to parse it
            result_str = template.render(context)

            # Try to parse the result as a Python literal (dict, list, etc.)
            # This handles cases where the expression evaluates to a dict/list
            # and Jinja2 converts it to a string representation
            if isinstance(result_str, str) and result_str.strip():
                # Try parsing as Python literal first (handles single quotes, None, True, False)
                # ast.literal_eval is safe and handles Python's repr format
                try:
                    return ast.literal_eval(result_str)
                except (ValueError, SyntaxError):
                    # If that fails, try parsing as JSON (handles double quotes)
                    try:
                        return json.loads(result_str)
                    except (json.JSONDecodeError, TypeError):
                        # If both fail, return as string
                        return result_str

            return result_str

        # If it's a dict (but not an expression marker), process recursively
        if isinstance(value, dict):
            processed_dict = {}
            has_expression_markers = False

            for key, val in value.items():
                # Check if this value is an expression marker before processing
                if isinstance(val, dict) and "__expr__" in val:
                    has_expression_markers = True
                # Recursively process nested values
                processed_dict[key] = self._process_parameter_value(val, context)

            # If we processed expression markers, return the processed dict directly
            # (don't treat the entire dict as a template string)
            if has_expression_markers:
                return processed_dict

            # After processing all nested values, check if the entire dict should be
            # treated as a template string (original behavior for backward compatibility)
            # Convert to JSON string for template rendering
            json_str = json.dumps(processed_dict)

            # Check if the JSON string contains template expressions
            if "{{" in json_str and "}}" in json_str:
                engine = ExpressionEngine()
                rendered = engine.render(json_str, context)
                try:
                    return json.loads(rendered)
                except (json.JSONDecodeError, TypeError):
                    return rendered

            return processed_dict

        # If it's a list, process each element recursively
        if isinstance(value, list):
            return [self._process_parameter_value(item, context) for item in value]

        # If it's a string, check if it contains template expressions
        if isinstance(value, str):
            if "{{" in value and "}}" in value:
                engine = ExpressionEngine()
                return engine.render(value, context)
            return value

        # For other types (int, float, bool, None), return as-is
        return value


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
