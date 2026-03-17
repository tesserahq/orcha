import pytest
from app.models.workflow import Workflow


@pytest.fixture(scope="function")
def test_workflow(db, faker, setup_user):
    """Create a test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "is_active": True,
        "created_by_id": setup_user.id,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


@pytest.fixture(scope="function")
def setup_workflow(db, faker, setup_user):
    """Create a test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "is_active": True,
        "created_by_id": setup_user.id,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


@pytest.fixture(scope="function")
def setup_another_workflow(db, faker, setup_user):
    """Create another test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "is_active": True,
        "created_by_id": setup_user.id,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow
