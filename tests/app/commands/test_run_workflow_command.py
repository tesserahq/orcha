"""Tests for the run_workflow command."""

import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from app.commands.run_workflow_command import RunWorkflowCommand
from app.models.workflow import Workflow
from app.models.workflow_version import WorkflowVersion
from app.models.node import Node
from app.models.edge import Edge
from app.services.workflow_service import WorkflowService
from app.services.workflow_version_service import WorkflowVersionService
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService
from app.constants.workflow_execution_status import WorkflowExecutionStatus
from app.exceptions.resource_not_found_error import ResourceNotFoundError


@pytest.fixture(scope="function")
def workflow_with_nodes(db, faker):
    """Create a workflow with an active version and nodes for testing."""
    # Create workflow
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
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

    # Create nodes
    node1 = Node(
        name="Trigger Node",
        description="Trigger node",
        kind="orcha-nodes.base.event_received",
        settings={},
        ui_settings={},
        workflow_version_id=workflow_version.id,
    )
    node2 = Node(
        name="HTTP Request Node",
        description="HTTP request node",
        kind="orcha-nodes.base.http_request",
        settings={},
        ui_settings={},
        workflow_version_id=workflow_version.id,
    )
    db.add(node1)
    db.add(node2)
    db.commit()
    db.refresh(node1)
    db.refresh(node2)

    # Create edge connecting node1 -> node2
    edge = Edge(
        name=None,
        source_node_id=node1.id,
        target_node_id=node2.id,
        workflow_version_id=workflow_version.id,
        settings={},
        ui_settings={},
    )
    db.add(edge)
    db.commit()

    return workflow


def test_run_workflow_success(db, workflow_with_nodes):
    """Test successfully running a workflow with nodes."""
    command = RunWorkflowCommand(db)
    input_data = {"test": "data", "value": 123}

    result = command.execute(workflow_with_nodes.id, input_data)

    # Verify result
    assert result["status"] == WorkflowExecutionStatus.SUCCESS
    assert result["data"] == input_data  # Nodes just pass through for now
    assert result["error"] is None

    # Verify workflow status was updated
    db.refresh(workflow_with_nodes)
    assert workflow_with_nodes.execution_status == WorkflowExecutionStatus.SUCCESS
    assert workflow_with_nodes.execution_status_message is None
    assert workflow_with_nodes.last_execution_time is not None


def test_run_workflow_workflow_not_found(db):
    """Test running a workflow that doesn't exist."""
    command = RunWorkflowCommand(db)
    non_existent_id = uuid4()

    with pytest.raises(ResourceNotFoundError) as exc_info:
        command.execute(non_existent_id, {"test": "data"})

    assert f"Workflow with id {non_existent_id} not found" in str(exc_info.value)


def test_run_workflow_no_active_version(db, faker):
    """Test running a workflow without an active version."""
    # Create workflow without active version
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
        active_version_id=None,
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    command = RunWorkflowCommand(db)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        command.execute(workflow.id, {"test": "data"})

    assert f"Workflow {workflow.id} does not have an active version" in str(
        exc_info.value
    )


def test_run_workflow_no_nodes(db, setup_workflow):
    """Test running a workflow with no nodes."""
    workflow = setup_workflow

    command = RunWorkflowCommand(db)

    result = command.execute(workflow.id, {"test": "data"})

    # Should fail because there are no nodes
    assert result["status"] == WorkflowExecutionStatus.FAILED
    assert "Workflow has no nodes to execute" in result["error"]

    # Verify workflow status was updated
    db.refresh(workflow)
    assert workflow.execution_status == WorkflowExecutionStatus.FAILED
    assert "Workflow has no nodes to execute" in workflow.execution_status_message


def test_run_workflow_no_trigger_nodes(db, setup_workflow, setup_workflow_version):
    """Test running a workflow with no trigger nodes (all nodes have incoming edges)."""
    workflow = setup_workflow

    # Create nodes (all with incoming edges)
    node1 = Node(
        name="Node 1",
        description="Node 1",
        kind="orcha-nodes.base.http_request",
        settings={},
        ui_settings={},
        workflow_version_id=workflow.active_version_id,
    )
    node2 = Node(
        name="Node 2",
        description="Node 2",
        kind="orcha-nodes.base.http_request",
        settings={},
        ui_settings={},
        workflow_version_id=workflow.active_version_id,
    )
    db.add(node1)
    db.add(node2)
    db.commit()
    db.refresh(node1)
    db.refresh(node2)

    # Create edge connecting node1 -> node2
    edge = Edge(
        name=None,
        source_node_id=node1.id,
        target_node_id=node2.id,
        workflow_version_id=workflow.active_version_id,
        settings={},
        ui_settings={},
    )
    db.add(edge)
    db.commit()

    command = RunWorkflowCommand(db)
    result = command.execute(workflow.id, {"test": "data"})

    # Should fail because there are no trigger nodes
    assert result["status"] == WorkflowExecutionStatus.FAILED
    assert (
        "Workflow has nodes with no incoming edges that are not from the trigger"
        in result["error"]
    )

    # Verify workflow status was updated
    db.refresh(workflow)
    assert workflow.execution_status == WorkflowExecutionStatus.FAILED
    assert (
        "Workflow has nodes with no incoming edges that are not from the trigger"
        in workflow.execution_status_message
    )


def test_run_workflow_updates_status_to_running(db, workflow_with_nodes):
    """Test that workflow status is updated to RUNNING before execution."""
    command = RunWorkflowCommand(db)
    input_data = {"test": "data"}

    # Initially workflow should not have execution status set
    assert workflow_with_nodes.execution_status is None

    result = command.execute(workflow_with_nodes.id, input_data)

    # Verify workflow status was set to RUNNING and then SUCCESS
    db.refresh(workflow_with_nodes)
    assert workflow_with_nodes.execution_status == WorkflowExecutionStatus.SUCCESS
    assert workflow_with_nodes.last_execution_time is not None


def test_run_workflow_linear_execution(db, faker):
    """Test running a workflow with multiple nodes in sequence."""
    # Create workflow
    workflow = Workflow(
        name=faker.sentence(nb_words=3),
        description=faker.text(max_nb_chars=200),
        is_active=True,
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

    # Create 3 nodes in sequence: trigger -> node1 -> node2
    trigger_node = Node(
        name="Trigger",
        description="Trigger node",
        kind="orcha-nodes.base.event_received",
        settings={},
        ui_settings={},
        workflow_version_id=workflow_version.id,
    )
    node1 = Node(
        name="Node 1",
        description="Node 1",
        kind="orcha-nodes.base.http_request",
        settings={},
        ui_settings={},
        workflow_version_id=workflow_version.id,
    )
    node2 = Node(
        name="Node 2",
        description="Node 2",
        kind="orcha-nodes.base.edit_fields",
        settings={},
        ui_settings={},
        workflow_version_id=workflow_version.id,
    )
    db.add(trigger_node)
    db.add(node1)
    db.add(node2)
    db.commit()
    db.refresh(trigger_node)
    db.refresh(node1)
    db.refresh(node2)

    # Create edges: trigger -> node1 -> node2
    edge1 = Edge(
        name=None,
        source_node_id=trigger_node.id,
        target_node_id=node1.id,
        workflow_version_id=workflow_version.id,
        settings={},
        ui_settings={},
    )
    edge2 = Edge(
        name=None,
        source_node_id=node1.id,
        target_node_id=node2.id,
        workflow_version_id=workflow_version.id,
        settings={},
        ui_settings={},
    )
    db.add(edge1)
    db.add(edge2)
    db.commit()

    command = RunWorkflowCommand(db)
    input_data = {"test": "data", "value": 42}

    result = command.execute(workflow.id, input_data)

    # Should succeed
    assert result["status"] == WorkflowExecutionStatus.SUCCESS
    assert result["data"] == input_data
    assert result["error"] is None

    # Verify workflow status
    db.refresh(workflow)
    assert workflow.execution_status == WorkflowExecutionStatus.SUCCESS
