"""Unit tests for the parameter expression engine.

These tests cover render_parameter and _process_value directly,
without requiring a database, full workflow execution, or node subclasses.
"""

from typing import Any, Dict

from app.constants.node_types import ExecutionContext, NodeResult
from app.nodes.parameter_renderer import (
    ParameterRenderer,
    _process_value,
    render_parameter,
)


def _context(json: Dict[str, Any] | None = None) -> ExecutionContext:
    """Build an ExecutionContext with the given json as the last node's output."""
    ctx = ExecutionContext(trigger_event={}, execution_id="test", triggered_by="manual")
    if json:
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
    """Build the expression context dict passed to _process_value."""
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
    assert _process_value(42, _ctx()) == 42


def test_float_is_returned_as_is():
    assert _process_value(3.14, _ctx()) == 3.14


def test_bool_is_returned_as_is():
    assert _process_value(True, _ctx()) is True


def test_none_is_returned_as_is():
    assert _process_value(None, _ctx()) is None


# ---------------------------------------------------------------------------
# Plain strings (no template syntax)
# ---------------------------------------------------------------------------


def test_plain_string_passthrough():
    assert _process_value("hello world", _ctx()) == "hello world"


def test_empty_string_passthrough():
    assert _process_value("", _ctx()) == ""


# ---------------------------------------------------------------------------
# String templates
# ---------------------------------------------------------------------------


def test_string_template_renders_json_value():
    ctx = _ctx(json={"account": "acme"})
    result = _process_value("{{ json.account }}", ctx)
    assert result == "acme"


def test_string_template_missing_variable_returns_empty_string():
    ctx = _ctx(json={})
    result = _process_value("{{ json.missing }}", ctx)
    assert result == ""


def test_string_template_interpolated_in_larger_string():
    ctx = _ctx(json={"name": "world"})
    result = _process_value("Hello, {{ json.name }}!", ctx)
    assert result == "Hello, world!"


# ---------------------------------------------------------------------------
# __expr__ marker — evaluates expression and returns Python object
# ---------------------------------------------------------------------------


def test_expr_marker_returns_dict():
    ctx = _ctx(json={"payload": {"key": "value"}})
    result = _process_value({"__expr__": "{{ json.payload }}"}, ctx)
    assert result == {"key": "value"}


def test_expr_marker_returns_list():
    ctx = _ctx(json={"tags": [1, 2, 3]})
    result = _process_value({"__expr__": "{{ json.tags }}"}, ctx)
    assert result == [1, 2, 3]


def test_expr_marker_json_items_key_collision():
    # KNOWN LIMITATION: the key name "items" collides with dict.items() method.
    # Jinja2 attribute access (json.items) resolves to the bound method, not the value.
    # Users must avoid naming keys after dict methods (keys, values, items, get, etc.)
    # or use bracket notation in the expression: json["items"].
    ctx = _ctx(json={"items": [1, 2, 3]})
    result = _process_value({"__expr__": "{{ json.items }}"}, ctx)
    # Returns the string form of the bound method — not the list
    assert result != [1, 2, 3]


def test_expr_marker_returns_string_when_not_parseable():
    ctx = _ctx(json={"greeting": "hello"})
    result = _process_value({"__expr__": "{{ json.greeting }}"}, ctx)
    assert result == "hello"


def test_expr_marker_with_non_string_expr_returns_value_unchanged():
    value = {"__expr__": 123}
    assert _process_value(value, _ctx()) is value


def test_expr_marker_with_none_result_returns_empty_string():
    # When expression renders to "" (empty), the marker should return "".
    ctx = _ctx(json={})
    result = _process_value({"__expr__": "{{ json.missing }}"}, ctx)
    assert result == ""


# ---------------------------------------------------------------------------
# Plain dicts (no expression markers)
# ---------------------------------------------------------------------------


def test_plain_dict_passthrough():
    value = {"a": 1, "b": "two"}
    assert _process_value(value, _ctx()) == {"a": 1, "b": "two"}


def test_dict_with_template_string_values_is_rendered():
    ctx = _ctx(json={"url": "https://example.com"})
    value = {"endpoint": "{{ json.url }}"}
    result = _process_value(value, ctx)
    assert result == {"endpoint": "https://example.com"}


def test_dict_without_templates_returned_unchanged():
    value = {"x": 1, "y": 2}
    result = _process_value(value, _ctx())
    assert result == {"x": 1, "y": 2}


def test_dict_with_expr_markers_processes_each_value():
    ctx = _ctx(json={"host": "api.example.com", "port": 443})
    value = {
        "host": {"__expr__": "{{ json.host }}"},
        "port": {"__expr__": "{{ json.port }}"},
    }
    result = _process_value(value, ctx)
    assert result == {"host": "api.example.com", "port": 443}


def test_dict_with_mixed_expr_and_plain_values():
    ctx = _ctx(json={"dynamic": "rendered"})
    value = {
        "static": "fixed",
        "dynamic": {"__expr__": "{{ json.dynamic }}"},
    }
    result = _process_value(value, ctx)
    assert result == {"static": "fixed", "dynamic": "rendered"}


# ---------------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------------


def test_list_of_plain_values_passthrough():
    assert _process_value([1, "two", True], _ctx()) == [1, "two", True]


def test_list_with_template_strings_renders_each():
    ctx = _ctx(json={"x": "hello"})
    result = _process_value(["{{ json.x }}", "plain"], ctx)
    assert result == ["hello", "plain"]


def test_list_with_expr_markers():
    ctx = _ctx(json={"obj": {"a": 1}})
    result = _process_value([{"__expr__": "{{ json.obj }}"}], ctx)
    assert result == [{"a": 1}]


def test_nested_list_in_dict():
    ctx = _ctx(json={"tags": ["a", "b"]})
    value = {"tags": {"__expr__": "{{ json.tags }}"}}
    result = _process_value(value, ctx)
    assert result == {"tags": ["a", "b"]}


# ---------------------------------------------------------------------------
# ParameterRenderer — context building and key lookup
# ---------------------------------------------------------------------------


def test_renderer_missing_key_returns_none():
    renderer = ParameterRenderer.for_node({}, _context(json={"foo": "bar"}))
    assert renderer.get("nonexistent") is None


def test_renderer_resolves_json_context():
    renderer = ParameterRenderer.for_node(
        {"url": "{{ json.base }}/path"},
        _context(json={"base": "https://api.example.com"}),
    )
    assert renderer.get("url") == "https://api.example.com/path"


def test_renderer_resolves_nodes_context():
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
    renderer = ParameterRenderer.for_node(
        {"account": "{{ nodes['Trigger'].account }}"}, ctx
    )
    assert renderer.get("account") == "acme"


def test_renderer_returns_primitive_unchanged():
    renderer = ParameterRenderer.for_node(
        {"count": 5, "project_id": "55e4f7b0-a447-430d-98f8-e650b0b708eb"},
        _context(),
    )
    assert renderer.get("count") == 5
    assert renderer.get("project_id") == "55e4f7b0-a447-430d-98f8-e650b0b708eb"


def test_render_parameter_convenience_function():
    ctx = _context(json={"value": 42})
    result = render_parameter({"__expr__": "{{ json.value }}"}, ctx)
    assert result == 42
