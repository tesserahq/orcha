"""Tests for the create_workflow command."""

import pytest
from sqlalchemy.orm import Session
from app.commands.create_workflow_command import CreateWorkflowCommand
from app.schemas.workflow import WorkflowCreate
from app.services.workflow_version_service import WorkflowVersionService


def test_create_workflow_creates_both_workflow_and_version(db: Session):
    """Test that the command creates both workflow and initial version."""
    workflow_data = WorkflowCreate(
        name="Test Workflow",
        description="Test description",
        trigger_event_type="test.event",
        trigger_event_filters={"field": "test", "value": "value"},
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


def test_create_workflow_inactive(db: Session):
    """Test that the command creates an inactive workflow version when workflow is inactive."""
    workflow_data = WorkflowCreate(
        name="Inactive Workflow",
        description="Inactive description",
        trigger_event_type="test.event",
        trigger_event_filters={"field": "test", "value": "value"},
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


def test_create_workflow_multiple_workflows(db: Session):
    """Test creating multiple workflows with versions."""
    workflow1_data = WorkflowCreate(
        name="Workflow 1",
        description="Description 1",
        trigger_event_type="event1",
        trigger_event_filters={"field": "test"},
        is_active=True,
    )

    workflow2_data = WorkflowCreate(
        name="Workflow 2",
        description="Description 2",
        trigger_event_type="event2",
        trigger_event_filters={"field": "test2"},
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
