"""Unit tests for the parameter expression engine in NodeDescription.

These tests cover _process_parameter_value and get_parsed_parameter directly,
without requiring a database or full workflow execution.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

import pytest

from app.constants.node_types import ExecutionContext, ExecutionData, NodeDescription

# ---------------------------------------------------------------------------
# Minimal concrete subclass — only exists to make NodeDescription instantiable
# ---------------------------------------------------------------------------


@dataclass
class _TestNode(NodeDescription):
    display_name: str = "Test"
    kind: str = "test.node"
    icon: str = ""
    icon_color: str = ""
    group: List[str] = field(default_factory=list)
    version: int = 1
    subtitle: str = ""
    description: str = ""
    defaults: Dict[str, Any] = field(default_factory=dict)

    def execute(self, context: ExecutionContext) -> ExecutionData:  # pragma: no cover
        return context.get_previous_output()


def _node(parameters: Dict[str, Any]) -> _TestNode:
    n = _TestNode()
    n.parameters = parameters
    return n


def _context(json: Dict[str, Any] | None = None) -> ExecutionContext:
    """Build an ExecutionContext with the given json as the last node's output."""
    ctx = ExecutionContext(trigger_event={}, execution_id="test", triggered_by="manual")
    if json:
        from app.constants.node_types import NodeResult
        ctx.append_result(
            NodeResult(
                node_id="prev",
                node_name="Prev Node",
                node_kind="test",
                status="success",
                input={},
                output=json,
                timestamp="2024-01-01T00:00:00+00:00",
            )
        )
    return ctx


def _ctx(json: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Build the expression context dict that get_parsed_parameter builds internally."""
    return {
        "json": json or {},
        "nodes": {},
        "execution": {"id": "test", "triggered_by": "manual"},
        "env": {},
    }


# ---------------------------------------------------------------------------
# Primitive / None passthrough
# ---------------------------------------------------------------------------


def test_int_is_returned_as_is():
    n = _node({})
    assert n._process_parameter_value(42, _ctx()) == 42


def test_float_is_returned_as_is():
    n = _node({})
    assert n._process_parameter_value(3.14, _ctx()) == 3.14


def test_bool_is_returned_as_is():
    n = _node({})
    assert n._process_parameter_value(True, _ctx()) is True


def test_none_is_returned_as_is():
    n = _node({})
    assert n._process_parameter_value(None, _ctx()) is None


# ---------------------------------------------------------------------------
# Plain strings (no template syntax)
# ---------------------------------------------------------------------------


def test_plain_string_passthrough():
    n = _node({})
    assert n._process_parameter_value("hello world", _ctx()) == "hello world"


def test_empty_string_passthrough():
    n = _node({})
    assert n._process_parameter_value("", _ctx()) == ""


# ---------------------------------------------------------------------------
# String templates
# ---------------------------------------------------------------------------


def test_string_template_renders_json_value():
    n = _node({})
    ctx = _ctx(json={"account": "acme"})
    result = n._process_parameter_value("{{ json.account }}", ctx)
    assert result == "acme"


def test_string_template_missing_variable_returns_empty_string():
    n = _node({})
    ctx = _ctx(json={})
    result = n._process_parameter_value("{{ json.missing }}", ctx)
    assert result == ""


def test_string_template_interpolated_in_larger_string():
    n = _node({})
    ctx = _ctx(json={"name": "world"})
    result = n._process_parameter_value("Hello, {{ json.name }}!", ctx)
    assert result == "Hello, world!"


# ---------------------------------------------------------------------------
# __expr__ marker — evaluates expression and returns Python object
# ---------------------------------------------------------------------------


def test_expr_marker_returns_dict():
    n = _node({})
    ctx = _ctx(json={"payload": {"key": "value"}})
    result = n._process_parameter_value({"__expr__": "{{ json.payload }}"}, ctx)
    assert result == {"key": "value"}


def test_expr_marker_returns_list():
    n = _node({})
    ctx = _ctx(json={"tags": [1, 2, 3]})
    result = n._process_parameter_value({"__expr__": "{{ json.tags }}"}, ctx)
    assert result == [1, 2, 3]


def test_expr_marker_json_items_key_collision():
    # KNOWN LIMITATION: the key name "items" collides with dict.items() method.
    # Jinja2 attribute access (json.items) resolves to the bound method, not the value.
    # Users must avoid naming keys after dict methods (keys, values, items, get, etc.)
    # or use bracket notation in the expression: json["items"].
    n = _node({})
    ctx = _ctx(json={"items": [1, 2, 3]})
    result = n._process_parameter_value({"__expr__": "{{ json.items }}"}, ctx)
    # Returns the string form of the bound method — not the list
    assert result != [1, 2, 3]


def test_expr_marker_returns_string_when_not_parseable():
    n = _node({})
    ctx = _ctx(json={"greeting": "hello"})
    result = n._process_parameter_value({"__expr__": "{{ json.greeting }}"}, ctx)
    assert result == "hello"


def test_expr_marker_with_non_string_expr_returns_value_unchanged():
    n = _node({})
    value = {"__expr__": 123}
    assert n._process_parameter_value(value, _ctx()) is value


def test_expr_marker_with_none_result_returns_empty_string():
    # When expression renders to "" (empty), the marker should return "".
    n = _node({})
    ctx = _ctx(json={})
    result = n._process_parameter_value({"__expr__": "{{ json.missing }}"}, ctx)
    assert result == ""


# ---------------------------------------------------------------------------
# Plain dicts (no expression markers)
# ---------------------------------------------------------------------------


def test_plain_dict_passthrough():
    n = _node({})
    value = {"a": 1, "b": "two"}
    assert n._process_parameter_value(value, _ctx()) == {"a": 1, "b": "two"}


def test_dict_with_template_string_values_is_rendered():
    n = _node({})
    ctx = _ctx(json={"url": "https://example.com"})
    value = {"endpoint": "{{ json.url }}"}
    result = n._process_parameter_value(value, ctx)
    assert result == {"endpoint": "https://example.com"}


def test_dict_without_templates_returned_unchanged():
    n = _node({})
    value = {"x": 1, "y": 2}
    result = n._process_parameter_value(value, _ctx())
    assert result == {"x": 1, "y": 2}


def test_dict_with_expr_markers_processes_each_value():
    n = _node({})
    ctx = _ctx(json={"host": "api.example.com", "port": 443})
    value = {
        "host": {"__expr__": "{{ json.host }}"},
        "port": {"__expr__": "{{ json.port }}"},
    }
    result = n._process_parameter_value(value, ctx)
    assert result == {"host": "api.example.com", "port": 443}


def test_dict_with_mixed_expr_and_plain_values():
    n = _node({})
    ctx = _ctx(json={"dynamic": "rendered"})
    value = {
        "static": "fixed",
        "dynamic": {"__expr__": "{{ json.dynamic }}"},
    }
    result = n._process_parameter_value(value, ctx)
    assert result == {"static": "fixed", "dynamic": "rendered"}


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------


def test_list_of_plain_values_passthrough():
    n = _node({})
    assert n._process_parameter_value([1, "two", True], _ctx()) == [1, "two", True]


def test_list_with_template_strings_renders_each():
    n = _node({})
    ctx = _ctx(json={"x": "hello"})
    result = n._process_parameter_value(["{{ json.x }}", "plain"], ctx)
    assert result == ["hello", "plain"]


def test_list_with_expr_markers():
    n = _node({})
    ctx = _ctx(json={"obj": {"a": 1}})
    result = n._process_parameter_value([{"__expr__": "{{ json.obj }}"}], ctx)
    assert result == [{"a": 1}]


def test_nested_list_in_dict():
    n = _node({})
    ctx = _ctx(json={"tags": ["a", "b"]})
    value = {"tags": {"__expr__": "{{ json.tags }}"}}
    result = n._process_parameter_value(value, ctx)
    assert result == {"tags": ["a", "b"]}


# ---------------------------------------------------------------------------
# get_parsed_parameter — context building
# ---------------------------------------------------------------------------


def test_get_parsed_parameter_missing_key_returns_none():
    n = _node({})
    ctx = _context(json={"foo": "bar"})
    assert n.get_parsed_parameter("nonexistent", ctx) is None


def test_get_parsed_parameter_resolves_json_context():
    n = _node({"url": "{{ json.base }}/path"})
    ctx = _context(json={"base": "https://api.example.com"})
    assert n.get_parsed_parameter("url", ctx) == "https://api.example.com/path"


def test_get_parsed_parameter_resolves_nodes_context():
    from app.constants.node_types import NodeResult

    ctx = ExecutionContext(trigger_event={}, execution_id="test", triggered_by="manual")
    ctx.append_result(
        NodeResult(
            node_id="n1",
            node_name="Trigger",
            node_kind="test",
            status="success",
            input={},
            output={"account": "acme"},
            timestamp="2024-01-01T00:00:00+00:00",
        )
    )
    n = _node({"account": "{{ nodes['Trigger'].account }}"})
    assert n.get_parsed_parameter("account", ctx) == "acme"


def test_get_parsed_parameter_returns_primitive_unchanged():
    n = _node({"count": 5})
    ctx = _context()
    assert n.get_parsed_parameter("count", ctx) == 5
