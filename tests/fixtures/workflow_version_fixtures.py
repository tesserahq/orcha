import pytest
from app.models.workflow_version import WorkflowVersion


@pytest.fixture(scope="function")
def test_workflow_version(db, faker, test_workflow):
    """Create a test workflow version for use in tests."""
    workflow_version_data = {
        "workflow_id": test_workflow.id,
        "version": 1,
        "is_active": True,
    }

    workflow_version = WorkflowVersion(**workflow_version_data)
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    return workflow_version


@pytest.fixture(scope="function")
def setup_workflow_version(db, faker, test_workflow):
    """Create a test workflow version for use in tests."""
    workflow_version_data = {
        "workflow_id": test_workflow.id,
        "version": 1,
        "is_active": True,
    }

    workflow_version = WorkflowVersion(**workflow_version_data)
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    return workflow_version


@pytest.fixture(scope="function")
def setup_another_workflow_version(db, faker, test_workflow):
    """Create another test workflow version for use in tests."""
    workflow_version_data = {
        "workflow_id": test_workflow.id,
        "version": 2,
        "is_active": False,
    }

    workflow_version = WorkflowVersion(**workflow_version_data)
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    return workflow_version
