import pytest
from app.models.node import Node


@pytest.fixture(scope="function")
def test_node(db, faker, test_workflow_version):
    """Create a test node for use in tests."""
    node_data = {
        "name": faker.word(),
        "description": faker.text(max_nb_chars=200),
        "kind": "action",
        "properties": [{"key": "value"}],
        "ui_settings": {"x": 100, "y": 200},
        "workflow_version_id": test_workflow_version.id,
    }

    node = Node(**node_data)
    db.add(node)
    db.commit()
    db.refresh(node)

    return node


@pytest.fixture(scope="function")
def setup_node(db, faker, test_workflow_version):
    """Create a test node for use in tests."""
    node_data = {
        "name": faker.word(),
        "description": faker.text(max_nb_chars=200),
        "kind": "trigger",
        "properties": [{"key": "value"}],
        "ui_settings": {"x": 100, "y": 200},
        "workflow_version_id": test_workflow_version.id,
    }

    node = Node(**node_data)
    db.add(node)
    db.commit()
    db.refresh(node)

    return node


@pytest.fixture(scope="function")
def setup_another_node(db, faker, test_workflow_version):
    """Create another test node for use in tests."""
    node_data = {
        "name": faker.word(),
        "description": faker.text(max_nb_chars=200),
        "kind": "condition",
        "properties": [{"key": "value2"}],
        "ui_settings": {"x": 300, "y": 400},
        "workflow_version_id": test_workflow_version.id,
    }

    node = Node(**node_data)
    db.add(node)
    db.commit()
    db.refresh(node)

    return node
