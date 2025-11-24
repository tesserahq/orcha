"""Tests for the create_workflow command."""

import pytest
from app.commands.create_workflow_command import CreateWorkflowCommand
from app.schemas.workflow import WorkflowCreate
from app.schemas.node import NodeCreatePayload
from app.services.workflow_version_service import WorkflowVersionService
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService


def test_create_workflow_creates_both_workflow_and_version(db):
    """Test that the command creates both workflow and initial version."""
    workflow_data = WorkflowCreate(
        name="Test Workflow",
        description="Test description",
        is_active=True,
    )

    workflow = CreateWorkflowCommand(db).execute(workflow_data)

    # Verify workflow was created
    assert workflow is not None
    assert workflow.name == "Test Workflow"
    assert workflow.description == "Test description"
    assert workflow.is_active is True

    # Verify version was created
    workflow_version_service = WorkflowVersionService(db)
    versions = workflow_version_service.get_workflow_versions_by_workflow(workflow.id)

    assert len(versions) == 1
    assert versions[0].version == 1
    assert versions[0].workflow_id == workflow.id
    assert versions[0].is_active is True

    # Verify active_version_id is included in the response
    assert hasattr(workflow, "active_version_id")
    assert workflow.active_version_id is not None
    assert workflow.active_version_id == versions[0].id


def test_create_workflow_inactive(db):
    """Test that the command creates an inactive workflow version when workflow is inactive."""
    workflow_data = WorkflowCreate(
        name="Inactive Workflow",
        description="Inactive description",
        is_active=False,
    )

    workflow = CreateWorkflowCommand(db).execute(workflow_data)

    # Verify workflow is inactive
    assert workflow.is_active is False

    # Verify version is also inactive
    workflow_version_service = WorkflowVersionService(db)
    versions = workflow_version_service.get_workflow_versions_by_workflow(workflow.id)

    assert len(versions) == 1
    assert versions[0].is_active is False

    # Verify active_version_id is included in the response
    assert hasattr(workflow, "active_version_id")
    assert workflow.active_version_id is not None
    assert workflow.active_version_id == versions[0].id


def test_create_workflow_multiple_workflows(db):
    """Test creating multiple workflows with versions."""
    workflow1_data = WorkflowCreate(
        name="Workflow 1",
        description="Description 1",
        is_active=True,
    )

    workflow2_data = WorkflowCreate(
        name="Workflow 2",
        description="Description 2",
        is_active=True,
    )

    workflow1 = CreateWorkflowCommand(db).execute(workflow1_data)
    workflow2 = CreateWorkflowCommand(db).execute(workflow2_data)

    assert workflow1.id != workflow2.id

    # Verify each workflow has its version
    workflow_version_service = WorkflowVersionService(db)
    versions1 = workflow_version_service.get_workflow_versions_by_workflow(workflow1.id)
    versions2 = workflow_version_service.get_workflow_versions_by_workflow(workflow2.id)

    assert len(versions1) == 1
    assert len(versions2) == 1
    assert versions1[0].workflow_id == workflow1.id
    assert versions2[0].workflow_id == workflow2.id
    assert versions1[0].version == 1
    assert versions2[0].version == 1

    # Verify active_version_id is included in both responses and matches the created versions
    assert hasattr(workflow1, "active_version_id")
    assert hasattr(workflow2, "active_version_id")
    assert workflow1.active_version_id is not None
    assert workflow2.active_version_id is not None
    assert workflow1.active_version_id == versions1[0].id
    assert workflow2.active_version_id == versions2[0].id
    assert workflow1.active_version_id != workflow2.active_version_id


def test_create_workflow_with_nodes_auto_edges(db):
    """Test that creating a workflow with nodes also creates edges between them."""
    node1 = NodeCreatePayload(
        name="Node 1",
        description="Test node 1",
        kind="action",
        properties=[{"a": 1}],
        ui_settings={"x": 1},
    )
    node2 = NodeCreatePayload(
        name="Node 2",
        description="Test node 2",
        kind="condition",
        properties=[{"b": 2}],
        ui_settings={"x": 2},
    )
    workflow_data = WorkflowCreate(
        name="Workflow with nodes",
        description="Test description",
        is_active=True,
        nodes=[node1, node2],
    )

    workflow = CreateWorkflowCommand(db).execute(workflow_data)

    # Verify workflow was created
    assert workflow is not None
    assert workflow.name == "Workflow with nodes"
    assert workflow.active_version_id is not None

    # Check that nodes and edges were created
    workflow_version_service = WorkflowVersionService(db)
    node_service = NodeService(db)
    edge_service = EdgeService(db)
    version_obj = workflow_version_service.get_workflow_version(
        workflow.active_version_id
    )
    all_nodes = node_service.get_nodes_by_workflow_version(version_obj.id)
    all_edges = edge_service.get_edges_by_workflow_version(version_obj.id)

    assert len(all_nodes) == 2
    assert len(all_edges) == 1

    # Ensure the edge connects Node 1 -> Node 2
    nodes_by_name = {n.name: n for n in all_nodes}
    created_edge = all_edges[0]
    assert created_edge.source_node_id == nodes_by_name["Node 1"].id
    assert created_edge.target_node_id == nodes_by_name["Node 2"].id
