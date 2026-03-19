"""Unit tests for ExecutionContext and NodeResult.

These tests cover the public interface of ExecutionContext in isolation —
no database, no workflow execution required.
"""

import pytest

from app.constants.node_types import ExecutionContext, ExecutionData, NodeResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result(name: str, output: dict) -> NodeResult:
    return NodeResult(
        node_id="id-" + name,
        node_name=name,
        node_kind="test.kind",
        status="success",
        input={},
        output=output,
        timestamp="2024-01-01T00:00:00+00:00",
    )


def _ctx(**kwargs) -> ExecutionContext:
    return ExecutionContext(
        trigger_event=kwargs.get("trigger_event", {}),
        execution_id=kwargs.get("execution_id", "exec-1"),
        triggered_by=kwargs.get("triggered_by", "manual"),
    )


# ---------------------------------------------------------------------------
# get_previous_output
# ---------------------------------------------------------------------------


def test_get_previous_output_empty_context_returns_empty_data():
    ctx = _ctx()
    result = ctx.get_previous_output()
    assert isinstance(result, ExecutionData)
    assert result.json == {}


def test_get_previous_output_returns_last_appended_output():
    ctx = _ctx()
    ctx.append_result(_result("A", {"x": 1}))
    ctx.append_result(_result("B", {"y": 2}))
    assert ctx.get_previous_output().json == {"y": 2}


def test_get_previous_output_returns_copy_not_reference():
    ctx = _ctx()
    ctx.append_result(_result("A", {"x": 1}))
    output = ctx.get_previous_output()
    output.json["x"] = 999
    # Mutating the returned copy must not affect the recorded result
    assert ctx.get_previous_output().json["x"] == 1


# ---------------------------------------------------------------------------
# get_node_output
# ---------------------------------------------------------------------------


def test_get_node_output_returns_correct_node():
    ctx = _ctx()
    ctx.append_result(_result("Alpha", {"a": 1}))
    ctx.append_result(_result("Beta", {"b": 2}))
    assert ctx.get_node_output("Alpha") == {"a": 1}
    assert ctx.get_node_output("Beta") == {"b": 2}


def test_get_node_output_unknown_name_returns_none():
    ctx = _ctx()
    ctx.append_result(_result("Alpha", {"a": 1}))
    assert ctx.get_node_output("Missing") is None


def test_get_node_output_empty_context_returns_none():
    ctx = _ctx()
    assert ctx.get_node_output("Any") is None


# ---------------------------------------------------------------------------
# to_expression_context
# ---------------------------------------------------------------------------


def test_to_expression_context_structure():
    ctx = _ctx(execution_id="abc", triggered_by="event")
    ctx.append_result(_result("Trigger", {"event_type": "order.created"}))
    expr = ctx.to_expression_context()

    assert expr["json"] == {"event_type": "order.created"}
    assert expr["nodes"] == {"Trigger": {"event_type": "order.created"}}
    assert expr["execution"] == {"id": "abc", "triggered_by": "event"}
    assert expr["env"] == {}


def test_to_expression_context_empty_context():
    ctx = _ctx()
    expr = ctx.to_expression_context()
    assert expr["json"] == {}
    assert expr["nodes"] == {}


def test_to_expression_context_nodes_keyed_by_name():
    ctx = _ctx()
    ctx.append_result(_result("Node One", {"k": "v1"}))
    ctx.append_result(_result("Node Two", {"k": "v2"}))
    expr = ctx.to_expression_context()
    assert "Node One" in expr["nodes"]
    assert "Node Two" in expr["nodes"]


# ---------------------------------------------------------------------------
# to_dict (serialization)
# ---------------------------------------------------------------------------


def test_to_dict_structure():
    ctx = _ctx(trigger_event={"event_type": "test"})
    ctx.append_result(_result("Trigger", {"out": 1}))
    d = ctx.to_dict()

    assert d["trigger_event"] == {"event_type": "test"}
    assert len(d["node_results"]) == 1
    nr = d["node_results"][0]
    assert nr["node_name"] == "Trigger"
    assert nr["output"] == {"out": 1}
    assert nr["status"] == "success"
    assert "timestamp" in nr


def test_to_dict_empty_node_results():
    ctx = _ctx(trigger_event={"foo": "bar"})
    d = ctx.to_dict()
    assert d["trigger_event"] == {"foo": "bar"}
    assert d["node_results"] == []


# ---------------------------------------------------------------------------
# trigger_event immutability
# ---------------------------------------------------------------------------


def test_trigger_event_property_is_read_only():
    ctx = _ctx(trigger_event={"original": True})
    with pytest.raises(AttributeError):
        ctx.trigger_event = {"mutated": True}  # type: ignore[misc]


def test_trigger_event_value_is_preserved():
    event = {"event_type": "order.created", "event_data": {"id": 42}}
    ctx = ExecutionContext(trigger_event=event, execution_id="e1", triggered_by="event")
    assert ctx.trigger_event == event
