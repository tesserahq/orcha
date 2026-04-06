"""Unit tests for NodeTreeExecutor.

These tests cover graph traversal, NodeResult assembly, and error recording
in isolation — no database or real node kinds required.
"""

import uuid
from unittest.mock import MagicMock

from app.constants.node_types import ExecutionContext, ExecutionData
from app.execution.node_tree_executor import NodeTreeExecutor

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _node(name: str, kind: str = "test.kind") -> MagicMock:
    node = MagicMock()
    node.id = uuid.uuid4()
    node.name = name
    node.kind = kind
    return node


def _edge(source, target) -> MagicMock:
    edge = MagicMock()
    edge.source_node_id = source.id
    edge.target_node_id = target.id
    return edge


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        trigger_event={},
        execution_id="exec-1",
        triggered_by="manual",
    )


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------


def test_successful_nodes_are_recorded():
    trigger = _node("Trigger")
    action = _node("Action")
    edge = _edge(trigger, action)

    def execute(node, ctx):
        return ExecutionData(json={"from": node.name})

    ctx = _ctx()
    result = NodeTreeExecutor(execute).run(trigger, [trigger, action], [edge], ctx)

    assert result is None
    results = ctx.to_dict()["node_results"]
    assert len(results) == 2
    assert results[0]["node_name"] == "Trigger"
    assert results[0]["status"] == "success"
    assert results[1]["node_name"] == "Action"
    assert results[1]["status"] == "success"


# ---------------------------------------------------------------------------
# Error path — output_data.error
# ---------------------------------------------------------------------------


def test_failed_node_is_recorded_with_error_status():
    trigger = _node("Trigger")
    action = _node("Action")
    edge = _edge(trigger, action)

    def execute(node, ctx):
        if node.name == "Action":
            return ExecutionData(json={}, error="HTTP 404: Not Found")
        return ExecutionData(json={"ok": True})

    ctx = _ctx()
    error_msg = NodeTreeExecutor(execute).run(trigger, [trigger, action], [edge], ctx)

    assert error_msg == "Action: HTTP 404: Not Found"
    results = ctx.to_dict()["node_results"]
    assert len(results) == 2

    trigger_result = results[0]
    assert trigger_result["node_name"] == "Trigger"
    assert trigger_result["status"] == "success"
    assert trigger_result["error_message"] is None

    action_result = results[1]
    assert action_result["node_name"] == "Action"
    assert action_result["status"] == "error"
    assert action_result["error_message"] == "HTTP 404: Not Found"
    assert action_result["output"] == {}


def test_failed_node_captures_input_snapshot():
    trigger = _node("Trigger")
    action = _node("Action")
    edge = _edge(trigger, action)

    def execute(node, ctx):
        if node.name == "Action":
            return ExecutionData(json={}, error="bad request")
        return ExecutionData(json={"key": "value"})

    ctx = _ctx()
    NodeTreeExecutor(execute).run(trigger, [trigger, action], [edge], ctx)

    action_result = ctx.to_dict()["node_results"][1]
    assert action_result["input"] == {"key": "value"}


def test_nodes_after_failed_node_are_not_executed():
    trigger = _node("Trigger")
    action = _node("Action")
    downstream = _node("Downstream")
    edges = [_edge(trigger, action), _edge(action, downstream)]

    executed = []

    def execute(node, ctx):
        executed.append(node.name)
        if node.name == "Action":
            return ExecutionData(json={}, error="failure")
        return ExecutionData(json={})

    ctx = _ctx()
    NodeTreeExecutor(execute).run(trigger, [trigger, action, downstream], edges, ctx)

    assert "Downstream" not in executed
    assert len(ctx.to_dict()["node_results"]) == 2  # Trigger + Action only


# ---------------------------------------------------------------------------
# Error path — exception raised
# ---------------------------------------------------------------------------


def test_exception_in_node_is_recorded_with_error_status():
    trigger = _node("Trigger")
    action = _node("Action")
    edge = _edge(trigger, action)

    def execute(node, ctx):
        if node.name == "Action":
            raise ValueError("unexpected crash")
        return ExecutionData(json={})

    ctx = _ctx()
    error_msg = NodeTreeExecutor(execute).run(trigger, [trigger, action], [edge], ctx)

    assert error_msg == "Action: unexpected crash"
    results = ctx.to_dict()["node_results"]
    assert len(results) == 2

    action_result = results[1]
    assert action_result["status"] == "error"
    assert action_result["error_message"] == "unexpected crash"
