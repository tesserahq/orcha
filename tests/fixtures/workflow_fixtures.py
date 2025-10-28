import pytest
from app.models.workflow import Workflow


@pytest.fixture(scope="function")
def test_workflow(db, faker):
    """Create a test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "trigger_event_type": faker.word(),
        "trigger_event_filters": {
            "field": faker.word(),
            "value": faker.word(),
        },
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
        "trigger_event_type": faker.word(),
        "trigger_event_filters": {
            "field": faker.word(),
            "value": faker.word(),
        },
        "is_active": True,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


@pytest.fixture(scope="function")
def setup_another_workflow(db, faker):
    """Create another test workflow for use in tests."""
    workflow_data = {
        "name": faker.sentence(nb_words=3),
        "description": faker.text(max_nb_chars=200),
        "trigger_event_type": faker.word(),
        "trigger_event_filters": {
            "field": faker.word(),
            "value": faker.word(),
        },
        "is_active": True,
    }

    workflow = Workflow(**workflow_data)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow
