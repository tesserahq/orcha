"""Tests for the execute_workflow command."""

import pytest
from uuid import UUID
from datetime import datetime
from app.commands.workflow import ExecuteWorkflowCommand
from app.models.workflow import Workflow
from app.models.workflow_version import WorkflowVersion
from app.models.node import Node
from app.models.edge import Edge
from app.exceptions.resource_not_found_error import ResourceNotFoundError


def get_test_event_payload(event_type: str = "test_event") -> dict:
    """Helper to create a valid test event payload for event_received nodes."""
    return {
        "source": "test",
        "spec_version": "1.0",
        "event_type": event_type,
        "event_data": {},
        "data_content_type": "application/json",
        "subject": "test",
        "time": datetime.utcnow().isoformat(),
    }


def test_execute_workflow_success(db, faker, setup_user):
    """Test successful execution of an active workflow with trigger nodes."""
    # Create workflow with active version
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Create workflow version
    workflow_version = WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        is_active=True,
    )
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    # Set active version on workflow
    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    # Create trigger node
    trigger_node = Node(
        name="Trigger Node",
        description="Test trigger",
        kind="orcha-nodes.base.event_received",
        properties=[{"event_type": "test_event"}],
        parameters={"event_test_payload": get_test_event_payload("test_event")},
        ui_settings={"x": 100, "y": 100},
        workflow_version_id=workflow_version.id,
    )
    db.add(trigger_node)
    db.commit()
    db.refresh(trigger_node)

    # Create another node (non-trigger)
    action_node = Node(
        name="Action Node",
        description="Test action",
        kind="orcha-nodes.base.test_action",
        properties=[],
        ui_settings={"x": 200, "y": 200},
        workflow_version_id=workflow_version.id,
    )
    db.add(action_node)
    db.commit()
    db.refresh(action_node)

    # Create edge from trigger to action
    edge = Edge(
        source_node_id=trigger_node.id,
        target_node_id=action_node.id,
        workflow_version_id=workflow_version.id,
        ui_settings={"type": "bezier"},
    )
    db.add(edge)
    db.commit()

    # Execute workflow
    command = ExecuteWorkflowCommand(db)
    initial_data = {"test_key": "test_value"}
    result = command.execute(workflow_id=workflow.id, initial_data=initial_data)

    # Verify result shape
    assert result is not None
    assert result["workflow_id"] == str(workflow.id)
    assert result["status"] == "completed"
    assert result["error_message"] is None
    assert "trigger_event" in result
    assert len(result["node_results"]) == 2  # Trigger + Action node

    # Verify nodes were executed in order
    node_results = result["node_results"]
    assert node_results[0]["node_name"] == "Trigger Node"
    assert node_results[0]["status"] == "success"
    assert node_results[1]["node_name"] == "Action Node"
    assert node_results[1]["status"] == "success"

    # Verify workflow status was updated
    db.refresh(workflow)
    assert workflow.last_execution_time is not None
    assert workflow.execution_status == "completed"
    assert workflow.execution_status_message == "Workflow executed successfully"


def test_execute_workflow_manual_execution(db, faker, setup_user):
    """Test execution of inactive workflow with manual=True."""
    # Create inactive workflow
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=False,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Create workflow version
    workflow_version = WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        is_active=True,
    )
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    # Create trigger node
    trigger_node = Node(
        name="Trigger Node",
        description="Test trigger",
        kind="orcha-nodes.base.event_received",
        properties=[{"event_type": "test_event"}],
        parameters={"event_test_payload": get_test_event_payload("test_event")},
        ui_settings={"x": 100, "y": 100},
        workflow_version_id=workflow_version.id,
    )
    db.add(trigger_node)
    db.commit()

    # Execute with manual=True
    command = ExecuteWorkflowCommand(db)
    result = command.execute(workflow_id=workflow.id, manual=True)

    # Verify execution succeeded
    assert result is not None
    assert result["status"] == "completed"


def test_execute_workflow_inactive_raises_error(db, faker, setup_user):
    """Test that executing inactive workflow without manual=True raises error."""
    # Create inactive workflow
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=False,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Create workflow version
    workflow_version = WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        is_active=True,
    )
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    # Create trigger node
    trigger_node = Node(
        name="Trigger Node",
        description="Test trigger",
        kind="orcha-nodes.base.event_received",
        properties=[{"event_type": "test_event"}],
        parameters={"event_test_payload": get_test_event_payload("test_event")},
        ui_settings={"x": 100, "y": 100},
        workflow_version_id=workflow_version.id,
    )
    db.add(trigger_node)
    db.commit()

    # Execute without manual=True should raise error
    command = ExecuteWorkflowCommand(db)
    with pytest.raises(ValueError) as exc_info:
        command.execute(workflow_id=workflow.id, manual=False)

    assert "not active" in str(exc_info.value).lower()


def test_execute_workflow_not_found_raises_error(db):
    """Test that executing non-existent workflow raises ResourceNotFoundError."""
    command = ExecuteWorkflowCommand(db)
    fake_id = UUID("00000000-0000-0000-0000-000000000000")

    with pytest.raises(ResourceNotFoundError) as exc_info:
        command.execute(workflow_id=fake_id)

    assert "not found" in str(exc_info.value).lower()


def test_execute_workflow_no_active_version_raises_error(db, faker, setup_user):
    """Test that executing workflow without active version raises error."""
    # Create workflow without active version
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Execute should raise error
    command = ExecuteWorkflowCommand(db)
    with pytest.raises(ValueError) as exc_info:
        command.execute(workflow_id=workflow.id)

    assert "no active version" in str(exc_info.value).lower()


def test_execute_workflow_no_trigger_nodes_raises_error(db, faker, setup_user):
    """Test that executing workflow without trigger nodes raises error."""
    # Create workflow with active version
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Create workflow version
    workflow_version = WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        is_active=True,
    )
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    # Create non-trigger node
    action_node = Node(
        name="Action Node",
        description="Test action",
        kind="orcha-nodes.base.test_action",
        properties=[],
        ui_settings={"x": 200, "y": 200},
        workflow_version_id=workflow_version.id,
    )
    db.add(action_node)
    db.commit()

    # Execute should raise error
    command = ExecuteWorkflowCommand(db)
    with pytest.raises(ValueError) as exc_info:
        command.execute(workflow_id=workflow.id)

    assert "no trigger nodes" in str(exc_info.value).lower()


def test_execute_workflow_data_flow(db, faker, setup_user):
    """Test that data flows correctly through nodes."""
    # Create workflow with active version
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    workflow_version = WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        is_active=True,
    )
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    # Create trigger node
    trigger_node = Node(
        name="Trigger Node",
        description="Test trigger",
        kind="orcha-nodes.base.event_received",
        properties=[{"event_type": "test_event"}],
        parameters={"event_test_payload": get_test_event_payload("test_event")},
        ui_settings={"x": 100, "y": 100},
        workflow_version_id=workflow_version.id,
    )
    db.add(trigger_node)
    db.commit()
    db.refresh(trigger_node)

    # Create action node
    action_node = Node(
        name="Action Node",
        description="Test action",
        kind="orcha-nodes.base.test_action",
        properties=[],
        ui_settings={"x": 200, "y": 200},
        workflow_version_id=workflow_version.id,
    )
    db.add(action_node)
    db.commit()
    db.refresh(action_node)

    # Create edge
    edge = Edge(
        source_node_id=trigger_node.id,
        target_node_id=action_node.id,
        workflow_version_id=workflow_version.id,
        ui_settings={"type": "bezier"},
    )
    db.add(edge)
    db.commit()

    # Execute with initial data
    command = ExecuteWorkflowCommand(db)
    initial_data = {"input": "test_data", "number": 42}
    result = command.execute(workflow_id=workflow.id, initial_data=initial_data)

    # trigger_event should contain the initial_data passed by the caller
    assert result["trigger_event"]["input"] == "test_data"
    assert result["trigger_event"]["number"] == 42

    # Trigger node output (event_received passes trigger_event as json)
    trigger_output = result["node_results"][0]["output"]
    assert trigger_output["input"] == "test_data"

    # Action node should have received data from trigger
    action_output = result["node_results"][1]["output"]
    assert action_output["input"] == "test_data"


def test_execute_workflow_multiple_trigger_nodes_raises_error(db, faker, setup_user):
    """Test that execution with multiple trigger nodes raises an error."""
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    workflow_version = WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        is_active=True,
    )
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    trigger_node_1 = Node(
        name="Trigger Node 1",
        description="Test trigger 1",
        kind="orcha-nodes.base.event_received",
        properties=[{"event_type": "event_1"}],
        parameters={"event_test_payload": get_test_event_payload("event_1")},
        ui_settings={"x": 100, "y": 100},
        workflow_version_id=workflow_version.id,
    )
    trigger_node_2 = Node(
        name="Trigger Node 2",
        description="Test trigger 2",
        kind="orcha-nodes.base.event_received",
        properties=[{"event_type": "event_2"}],
        parameters={"event_test_payload": get_test_event_payload("event_2")},
        ui_settings={"x": 100, "y": 200},
        workflow_version_id=workflow_version.id,
    )
    db.add(trigger_node_1)
    db.add(trigger_node_2)
    db.commit()

    command = ExecuteWorkflowCommand(db)
    with pytest.raises(ValueError) as exc_info:
        command.execute(workflow_id=workflow.id)

    assert "more than one trigger" in str(exc_info.value).lower()


def test_execute_workflow_no_nodes_raises_error(db, faker, setup_user):
    """Test that executing workflow version with no nodes raises error."""
    # Create workflow with active version
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
        created_by_id=setup_user.id,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Create workflow version (but no nodes)
    workflow_version = WorkflowVersion(
        workflow_id=workflow.id,
        version=1,
        is_active=True,
    )
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    # Execute should raise error
    command = ExecuteWorkflowCommand(db)
    with pytest.raises(ValueError) as exc_info:
        command.execute(workflow_id=workflow.id)

    assert "no nodes" in str(exc_info.value).lower()
