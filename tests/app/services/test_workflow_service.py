import pytest
from uuid import uuid4
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate
from app.services.workflow_service import WorkflowService


@pytest.fixture
def sample_workflow_data():
    return {
        "name": "Test Workflow",
        "description": "This is a test workflow",
        "is_active": True,
    }


def test_create_workflow(db, sample_workflow_data):
    """Test creating a new workflow."""
    workflow_create = WorkflowCreate(**sample_workflow_data)
    workflow = WorkflowService(db).create_workflow(workflow_create)

    assert workflow.id is not None
    assert workflow.name == sample_workflow_data["name"]
    assert workflow.description == sample_workflow_data["description"]
    assert workflow.is_active == sample_workflow_data["is_active"]
    assert workflow.created_at is not None
    assert workflow.updated_at is not None


def test_get_workflow(db, test_workflow):
    """Test retrieving a workflow by ID."""
    retrieved_workflow = WorkflowService(db).get_workflow(test_workflow.id)

    assert retrieved_workflow is not None
    assert retrieved_workflow.id == test_workflow.id
    assert retrieved_workflow.name == test_workflow.name


def test_get_workflows(db, test_workflow):
    """Test retrieving all workflows."""
    workflows = WorkflowService(db).get_workflows()

    assert len(workflows) >= 1
    assert any(w.id == test_workflow.id for w in workflows)


def test_get_active_workflows(db, test_workflow):
    """Test retrieving active workflows."""
    workflows = WorkflowService(db).get_active_workflows()

    assert len(workflows) >= 1
    assert any(w.id == test_workflow.id for w in workflows)
    assert all(w.is_active for w in workflows)


def test_update_workflow(db, test_workflow):
    """Test updating a workflow."""
    update_data = {
        "name": "Updated Workflow Name",
        "description": "Updated description",
        "is_active": False,
    }
    workflow_update = WorkflowUpdate(**update_data)

    updated_workflow = WorkflowService(db).update_workflow(
        test_workflow.id, workflow_update
    )

    assert updated_workflow is not None
    assert updated_workflow.id == test_workflow.id
    assert updated_workflow.name == update_data["name"]
    assert updated_workflow.description == update_data["description"]
    assert updated_workflow.is_active == update_data["is_active"]


def test_delete_workflow(db, test_workflow):
    """Test soft deleting a workflow."""
    workflow_service = WorkflowService(db)
    success = workflow_service.delete_workflow(test_workflow.id)

    assert success is True
    deleted_workflow = workflow_service.get_workflow(test_workflow.id)
    assert deleted_workflow is None


def test_get_deleted_workflow(db, test_workflow):
    """Test retrieving a soft-deleted workflow."""
    workflow_service = WorkflowService(db)
    workflow_service.delete_workflow(test_workflow.id)

    deleted_workflow = workflow_service.get_deleted_workflow(test_workflow.id)

    assert deleted_workflow is not None
    assert deleted_workflow.id == test_workflow.id
    assert deleted_workflow.deleted_at is not None


def test_restore_workflow(db, test_workflow):
    """Test restoring a soft-deleted workflow."""
    workflow_service = WorkflowService(db)
    workflow_service.delete_workflow(test_workflow.id)

    assert workflow_service.get_workflow(test_workflow.id) is None

    success = workflow_service.restore_workflow(test_workflow.id)

    assert success is True
    restored_workflow = workflow_service.get_workflow(test_workflow.id)
    assert restored_workflow is not None
    assert restored_workflow.id == test_workflow.id


def test_hard_delete_workflow(db, test_workflow):
    """Test permanently deleting a workflow."""
    workflow_service = WorkflowService(db)
    workflow_id = test_workflow.id

    success = workflow_service.hard_delete_workflow(workflow_id)

    assert success is True
    deleted_workflow = workflow_service.get_deleted_workflow(workflow_id)
    assert deleted_workflow is None


def test_get_deleted_workflows(db, test_workflow):
    """Test retrieving all soft-deleted workflows."""
    workflow_service = WorkflowService(db)
    workflow_service.delete_workflow(test_workflow.id)

    deleted_workflows = workflow_service.get_deleted_workflows()

    assert len(deleted_workflows) >= 1
    assert any(w.id == test_workflow.id for w in deleted_workflows)


def test_search_workflows_with_filters(db, test_workflow):
    """Test searching workflows with filters."""
    filters = {"name": {"operator": "ilike", "value": f"%{test_workflow.name}%"}}
    results = WorkflowService(db).search(filters)

    assert isinstance(results, list)
    assert any(workflow.id == test_workflow.id for workflow in results)


def test_workflow_not_found_cases(db):
    """Test various not found cases."""
    workflow_service = WorkflowService(db)
    non_existent_id = uuid4()

    assert workflow_service.get_workflow(non_existent_id) is None

    update_data = {"name": "Updated Name"}
    workflow_update = WorkflowUpdate(**update_data)

    assert workflow_service.update_workflow(non_existent_id, workflow_update) is None

    assert workflow_service.delete_workflow(non_existent_id) is False

    assert workflow_service.restore_workflow(non_existent_id) is False

    assert workflow_service.hard_delete_workflow(non_existent_id) is False


def test_toggle_workflow_active_status(db, test_workflow):
    """Test toggling workflow active status."""
    workflow_service = WorkflowService(db)
    original_status = test_workflow.is_active

    toggled_workflow = workflow_service.toggle_workflow_active_status(test_workflow.id)

    assert toggled_workflow is not None
    assert toggled_workflow.is_active != original_status

    # Toggle back
    toggled_workflow = workflow_service.toggle_workflow_active_status(test_workflow.id)
    assert toggled_workflow.is_active == original_status


def test_get_workflows_query(db, test_workflow):
    """Test getting workflows query object."""

    select_stmt = WorkflowService(db).get_workflows_query()
    workflows = db.execute(select_stmt).scalars().all()

    assert len(workflows) >= 1
    assert any(w.id == test_workflow.id for w in workflows)
