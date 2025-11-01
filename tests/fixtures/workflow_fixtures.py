from app.models.workflow_version import WorkflowVersion
import pytest
from app.models.workflow import Workflow


@pytest.fixture(scope="function")
def test_workflow(db, faker):
    """Create a test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "is_active": True,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


@pytest.fixture(scope="function")
def setup_workflow(db, faker):
    """Create a test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "is_active": True,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    workflow_version_data = {
        "workflow_id": workflow.id,
        "version": 1,
        "is_active": True,
    }

    workflow_version = WorkflowVersion(**workflow_version_data)
    db.add(workflow_version)
    db.commit()
    db.refresh(workflow_version)

    workflow.active_version_id = workflow_version.id
    db.commit()
    db.refresh(workflow)

    return workflow


@pytest.fixture(scope="function")
def setup_another_workflow(db, faker):
    """Create another test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "is_active": True,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow
