import pytest
from app.models.edge import Edge


@pytest.fixture(scope="function")
def test_edge(db, faker, test_node, setup_node):
    """Create a test edge for use in tests."""
    edge_data = {
        "name": faker.word(),
        "source_node_id": test_node.id,
        "target_node_id": setup_node.id,
        "workflow_version_id": test_node.workflow_version_id,
        "properties": [{"key": "value"}],
        "ui_settings": {"type": "bezier"},
    }

    edge = Edge(**edge_data)
    db.add(edge)
    db.commit()
    db.refresh(edge)

    return edge


@pytest.fixture(scope="function")
def setup_edge(db, faker, setup_node, setup_another_node):
    """Create a test edge for use in tests."""
    edge_data = {
        "name": faker.word(),
        "source_node_id": setup_node.id,
        "target_node_id": setup_another_node.id,
        "workflow_version_id": setup_node.workflow_version_id,
        "properties": [{"key": "value"}],
        "ui_settings": {"type": "straight"},
    }

    edge = Edge(**edge_data)
    db.add(edge)
    db.commit()
    db.refresh(edge)

    return edge


@pytest.fixture(scope="function")
def setup_another_edge(db, faker, test_node, setup_another_node):
    """Create another test edge for use in tests."""
    edge_data = {
        "name": faker.word(),
        "source_node_id": test_node.id,
        "target_node_id": setup_another_node.id,
        "workflow_version_id": test_node.workflow_version_id,
        "properties": [{"key": "value2"}],
        "ui_settings": {"type": "step"},
    }

    edge = Edge(**edge_data)
    db.add(edge)
    db.commit()
    db.refresh(edge)

    return edge
