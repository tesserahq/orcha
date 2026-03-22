"""Standalone parameter rendering engine for workflow nodes.

Extracts the expression-evaluation logic that previously lived on
NodeDescription, making it callable without any inheritance.
"""

from __future__ import annotations

import ast
import json
from typing import Any, Dict, Optional

from tessera_sdk.infra.expressions import ExpressionEngine

from app.constants.node_types import ExecutionContext


def render_parameter(value: Any, context: ExecutionContext) -> Any:
    """Render a single parameter value against an ExecutionContext.

    Convenience entry point for callers that already hold a raw value.
    Also the primary entry point for tests — no node subclass needed.
    """
    return _process_value(value, context.to_expression_context())


class ParameterRenderer:
    """Renders a node's parameters against a fixed ExecutionContext.

    Construct via ParameterRenderer.for_node(parameters, context).
    to_expression_context() is called exactly once at construction and
    reused for all subsequent .get() / .get_all() calls.
    """

    def __init__(
        self, parameters: Dict[str, Any], expr_context: Dict[str, Any]
    ) -> None:
        self._parameters = parameters
        self._expr_context = expr_context

    @classmethod
    def for_node(
        cls, parameters: Dict[str, Any], context: ExecutionContext
    ) -> "ParameterRenderer":
        """Primary factory. Call once at the top of a node's execute()."""
        return cls(parameters, context.to_expression_context())

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Render and return a single parameter value.

        Returns default if the key is absent from parameters.
        """
        raw = self._parameters.get(key)
        if raw is None:
            return default
        return _process_value(raw, self._expr_context)

    def get_all(self, *keys: str) -> Dict[str, Any]:
        """Render and return multiple parameters in one call.

        Returns a dict keyed by the parameter names. Absent keys get None.
        """
        return {key: self.get(key) for key in keys}


def _process_value(value: Any, context: Dict[str, Any]) -> Any:
    """Recursively resolve a parameter value against an expression context dict."""
    # __expr__ marker — evaluate and coerce back to a Python object
    if isinstance(value, dict) and "__expr__" in value:
        expr_str = value["__expr__"]
        if not isinstance(expr_str, str):
            return value

        engine = ExpressionEngine()
        result_str = engine.env.from_string(expr_str).render(context)

        if isinstance(result_str, str) and result_str.strip():
            try:
                return ast.literal_eval(result_str)
            except (ValueError, SyntaxError):
                try:
                    return json.loads(result_str)
                except (json.JSONDecodeError, TypeError):
                    return result_str

        return result_str

    # Plain dict — recurse into values
    if isinstance(value, dict):
        processed: Dict[str, Any] = {}
        has_expr = False
        for k, v in value.items():
            if isinstance(v, dict) and "__expr__" in v:
                has_expr = True
            processed[k] = _process_value(v, context)

        if has_expr:
            return processed

        json_str = json.dumps(processed)
        if "{{" in json_str and "}}" in json_str:
            engine = ExpressionEngine()
            rendered = engine.render(json_str, context)
            try:
                return json.loads(rendered)
            except (json.JSONDecodeError, TypeError):
                return rendered

        return processed

    # List — recurse into each element
    if isinstance(value, list):
        return [_process_value(item, context) for item in value]

    # String — render if it contains template markers
    if isinstance(value, str):
        if "{{" in value and "}}" in value:
            return ExpressionEngine().render(value, context)
        return value

    # Primitives (int, float, bool, None) — pass through unchanged
    return value
