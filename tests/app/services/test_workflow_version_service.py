import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.workflow_version import (
    WorkflowVersionCreate,
    WorkflowVersionUpdate,
)
from app.services.workflow_version_service import WorkflowVersionService


@pytest.fixture
def sample_workflow_version_data(test_workflow):
    return {
        "workflow_id": test_workflow.id,
        "version": 1,
        "is_active": True,
    }


def test_create_workflow_version_auto_increment(db, test_workflow):
    """Test creating workflow versions with auto-increment."""
    service = WorkflowVersionService(db)

    # Create first version without specifying version
    version_data = {"workflow_id": test_workflow.id, "is_active": True}
    version1 = service.create_workflow_version(WorkflowVersionCreate(**version_data))
    assert version1.version == 1

    # The unique constraint only allows one active and one inactive version
    # So we can only test with specific version numbers
    # Create second version with explicit version and inactive
    version2_data = {"workflow_id": test_workflow.id, "is_active": False, "version": 2}
    version2 = service.create_workflow_version(WorkflowVersionCreate(**version2_data))
    assert version2.version == 2

    # Verify the auto-increment by checking get_next_version
    next_version = service.get_next_version(test_workflow.id)
    assert next_version == 3  # Should be 3 after versions 1 and 2


def test_create_workflow_version(db, sample_workflow_version_data):
    """Test creating a new workflow version."""
    workflow_version_create = WorkflowVersionCreate(**sample_workflow_version_data)
    workflow_version = WorkflowVersionService(db).create_workflow_version(
        workflow_version_create
    )

    assert workflow_version.id is not None
    assert workflow_version.workflow_id == sample_workflow_version_data["workflow_id"]
    assert workflow_version.version == sample_workflow_version_data["version"]
    assert workflow_version.is_active == sample_workflow_version_data["is_active"]
    assert workflow_version.created_at is not None
    assert workflow_version.updated_at is not None


def test_get_workflow_version(db, test_workflow_version):
    """Test retrieving a workflow version by ID."""
    retrieved_workflow_version = WorkflowVersionService(db).get_workflow_version(
        test_workflow_version.id
    )

    assert retrieved_workflow_version is not None
    assert retrieved_workflow_version.id == test_workflow_version.id
    assert retrieved_workflow_version.workflow_id == test_workflow_version.workflow_id


def test_get_workflow_versions(db, test_workflow_version):
    """Test retrieving all workflow versions."""
    workflow_versions = WorkflowVersionService(db).get_workflow_versions()

    assert len(workflow_versions) >= 1
    assert any(wv.id == test_workflow_version.id for wv in workflow_versions)


def test_get_workflow_versions_by_workflow(db, test_workflow_version, test_workflow):
    """Test retrieving workflow versions by workflow ID."""
    workflow_versions = WorkflowVersionService(db).get_workflow_versions_by_workflow(
        test_workflow.id
    )

    assert len(workflow_versions) >= 1
    assert any(wv.id == test_workflow_version.id for wv in workflow_versions)
    assert all(wv.workflow_id == test_workflow.id for wv in workflow_versions)


def test_get_active_workflow_versions(db, test_workflow_version):
    """Test retrieving active workflow versions."""
    workflow_versions = WorkflowVersionService(db).get_active_workflow_versions()

    assert len(workflow_versions) >= 1
    assert any(wv.id == test_workflow_version.id for wv in workflow_versions)
    assert all(wv.is_active == True for wv in workflow_versions)


def test_update_workflow_version(db, test_workflow_version):
    """Test updating a workflow version."""
    update_data = {
        "version": 2,
        "is_active": False,
    }
    workflow_version_update = WorkflowVersionUpdate(**update_data)

    updated_workflow_version = WorkflowVersionService(db).update_workflow_version(
        test_workflow_version.id, workflow_version_update
    )

    assert updated_workflow_version is not None
    assert updated_workflow_version.id == test_workflow_version.id
    assert updated_workflow_version.version == update_data["version"]
    assert updated_workflow_version.is_active == update_data["is_active"]


def test_delete_workflow_version(db, test_workflow_version):
    """Test soft deleting a workflow version."""
    workflow_version_service = WorkflowVersionService(db)
    success = workflow_version_service.delete_workflow_version(test_workflow_version.id)

    assert success is True
    deleted_workflow_version = workflow_version_service.get_workflow_version(
        test_workflow_version.id
    )
    assert deleted_workflow_version is None


def test_get_deleted_workflow_version(db, test_workflow_version):
    """Test retrieving a soft-deleted workflow version."""
    workflow_version_service = WorkflowVersionService(db)
    workflow_version_service.delete_workflow_version(test_workflow_version.id)

    deleted_workflow_version = workflow_version_service.get_deleted_workflow_version(
        test_workflow_version.id
    )

    assert deleted_workflow_version is not None
    assert deleted_workflow_version.id == test_workflow_version.id
    assert deleted_workflow_version.deleted_at is not None


def test_restore_workflow_version(db, test_workflow_version):
    """Test restoring a soft-deleted workflow version."""
    workflow_version_service = WorkflowVersionService(db)
    workflow_version_service.delete_workflow_version(test_workflow_version.id)

    assert (
        workflow_version_service.get_workflow_version(test_workflow_version.id) is None
    )

    success = workflow_version_service.restore_workflow_version(
        test_workflow_version.id
    )

    assert success is True
    restored_workflow_version = workflow_version_service.get_workflow_version(
        test_workflow_version.id
    )
    assert restored_workflow_version is not None
    assert restored_workflow_version.id == test_workflow_version.id


def test_hard_delete_workflow_version(db, test_workflow_version):
    """Test permanently deleting a workflow version."""
    workflow_version_service = WorkflowVersionService(db)
    workflow_version_id = test_workflow_version.id

    success = workflow_version_service.hard_delete_workflow_version(workflow_version_id)

    assert success is True
    deleted_workflow_version = workflow_version_service.get_deleted_workflow_version(
        workflow_version_id
    )
    assert deleted_workflow_version is None


def test_get_deleted_workflow_versions(db, test_workflow_version):
    """Test retrieving all soft-deleted workflow versions."""
    workflow_version_service = WorkflowVersionService(db)
    workflow_version_service.delete_workflow_version(test_workflow_version.id)

    deleted_workflow_versions = workflow_version_service.get_deleted_workflow_versions()

    assert len(deleted_workflow_versions) >= 1
    assert any(wv.id == test_workflow_version.id for wv in deleted_workflow_versions)


def test_search_workflow_versions_with_filters(db, test_workflow_version):
    """Test searching workflow versions with filters."""
    filters = {"version": test_workflow_version.version}
    results = WorkflowVersionService(db).search(filters)

    assert isinstance(results, list)
    assert any(
        workflow_version.id == test_workflow_version.id for workflow_version in results
    )

    filters = {"version": {"operator": ">=", "value": 1}}
    results = WorkflowVersionService(db).search(filters)

    assert len(results) >= 1


def test_workflow_version_not_found_cases(db):
    """Test various not found cases."""
    workflow_version_service = WorkflowVersionService(db)
    non_existent_id = uuid4()

    assert workflow_version_service.get_workflow_version(non_existent_id) is None

    update_data = {"version": 2}
    workflow_version_update = WorkflowVersionUpdate(**update_data)
    assert (
        workflow_version_service.update_workflow_version(
            non_existent_id, workflow_version_update
        )
        is None
    )

    assert workflow_version_service.delete_workflow_version(non_existent_id) is False

    assert workflow_version_service.restore_workflow_version(non_existent_id) is False

    assert (
        workflow_version_service.hard_delete_workflow_version(non_existent_id) is False
    )


def test_toggle_workflow_version_active_status(db, test_workflow_version):
    """Test toggling workflow version active status."""
    workflow_version_service = WorkflowVersionService(db)
    original_status = test_workflow_version.is_active

    toggled_workflow_version = (
        workflow_version_service.toggle_workflow_version_active_status(
            test_workflow_version.id
        )
    )

    assert toggled_workflow_version is not None
    assert toggled_workflow_version.is_active != original_status

    # Toggle back
    toggled_workflow_version = (
        workflow_version_service.toggle_workflow_version_active_status(
            test_workflow_version.id
        )
    )
    assert toggled_workflow_version.is_active == original_status


def test_get_workflow_versions_query(db, test_workflow_version):
    """Test getting workflow versions query object."""
    from sqlalchemy import select

    select_stmt = WorkflowVersionService(db).get_workflow_versions_query()
    workflow_versions = db.execute(select_stmt).scalars().all()

    assert len(workflow_versions) >= 1
    assert any(wv.id == test_workflow_version.id for wv in workflow_versions)
