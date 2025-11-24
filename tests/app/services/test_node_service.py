import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.node import NodeCreate, NodeUpdate
from app.services.node_service import NodeService


@pytest.fixture
def sample_node_data(test_workflow_version):
    return {
        "name": "Test Node",
        "description": "This is a test node",
        "kind": "action",
        "properties": [{"key": "value"}],
        "ui_settings": {"x": 100, "y": 200},
        "workflow_version_id": test_workflow_version.id,
    }


def test_create_node(db, sample_node_data):
    """Test creating a new node."""
    node_create = NodeCreate(**sample_node_data)
    node = NodeService(db).create_node(node_create)

    assert node.id is not None
    assert node.name == sample_node_data["name"]
    assert node.description == sample_node_data["description"]
    assert node.kind == sample_node_data["kind"]
    assert node.properties == sample_node_data["properties"]
    assert node.ui_settings == sample_node_data["ui_settings"]
    assert node.workflow_version_id == sample_node_data["workflow_version_id"]
    assert node.created_at is not None
    assert node.updated_at is not None


def test_get_node(db, test_node):
    """Test retrieving a node by ID."""
    retrieved_node = NodeService(db).get_node(test_node.id)

    assert retrieved_node is not None
    assert retrieved_node.id == test_node.id
    assert retrieved_node.name == test_node.name


def test_get_nodes(db, test_node):
    """Test retrieving all nodes."""
    nodes = NodeService(db).get_nodes()

    assert len(nodes) >= 1
    assert any(n.id == test_node.id for n in nodes)


def test_get_nodes_by_workflow_version(db, test_node):
    """Test retrieving nodes by workflow version."""
    nodes = NodeService(db).get_nodes_by_workflow_version(test_node.workflow_version_id)

    assert len(nodes) >= 1
    assert any(n.id == test_node.id for n in nodes)
    assert all(n.workflow_version_id == test_node.workflow_version_id for n in nodes)


def test_get_nodes_by_kind(db, test_node):
    """Test retrieving nodes by kind."""
    nodes = NodeService(db).get_nodes_by_kind(test_node.kind)

    assert len(nodes) >= 1
    assert any(n.id == test_node.id for n in nodes)
    assert all(n.kind == test_node.kind for n in nodes)


def test_update_node(db, test_node):
    """Test updating a node."""
    update_data = {
        "name": "Updated Node Name",
        "description": "Updated description",
    }
    node_update = NodeUpdate(**update_data)

    updated_node = NodeService(db).update_node(test_node.id, node_update)

    assert updated_node is not None
    assert updated_node.id == test_node.id
    assert updated_node.name == update_data["name"]
    assert updated_node.description == update_data["description"]


def test_delete_node(db, test_node):
    """Test soft deleting a node."""
    node_service = NodeService(db)
    success = node_service.delete_node(test_node.id)

    assert success is True
    deleted_node = node_service.get_node(test_node.id)
    assert deleted_node is None


def test_get_deleted_node(db, test_node):
    """Test retrieving a soft-deleted node."""
    node_service = NodeService(db)
    node_service.delete_node(test_node.id)

    deleted_node = node_service.get_deleted_node(test_node.id)

    assert deleted_node is not None
    assert deleted_node.id == test_node.id
    assert deleted_node.deleted_at is not None


def test_restore_node(db, test_node):
    """Test restoring a soft-deleted node."""
    node_service = NodeService(db)
    node_service.delete_node(test_node.id)

    assert node_service.get_node(test_node.id) is None

    success = node_service.restore_node(test_node.id)

    assert success is True
    restored_node = node_service.get_node(test_node.id)
    assert restored_node is not None
    assert restored_node.id == test_node.id


def test_hard_delete_node(db, test_node):
    """Test permanently deleting a node."""
    node_service = NodeService(db)
    node_id = test_node.id

    success = node_service.hard_delete_node(node_id)

    assert success is True
    deleted_node = node_service.get_deleted_node(node_id)
    assert deleted_node is None


def test_get_deleted_nodes(db, test_node):
    """Test retrieving all soft-deleted nodes."""
    node_service = NodeService(db)
    node_service.delete_node(test_node.id)

    deleted_nodes = node_service.get_deleted_nodes()

    assert len(deleted_nodes) >= 1
    assert any(n.id == test_node.id for n in deleted_nodes)


def test_search_nodes_with_filters(db, test_node):
    """Test searching nodes with filters."""
    filters = {"name": {"operator": "ilike", "value": f"%{test_node.name}%"}}
    results = NodeService(db).search(filters)

    assert isinstance(results, list)
    assert any(node.id == test_node.id for node in results)

    filters = {"kind": test_node.kind}
    results = NodeService(db).search(filters)

    assert len(results) >= 1
    assert results[0].id == test_node.id


def test_node_not_found_cases(db):
    """Test various not found cases."""
    node_service = NodeService(db)
    non_existent_id = uuid4()

    assert node_service.get_node(non_existent_id) is None

    update_data = {"name": "Updated Name"}
    node_update = NodeUpdate(**update_data)
    assert node_service.update_node(non_existent_id, node_update) is None

    assert node_service.delete_node(non_existent_id) is False

    assert node_service.restore_node(non_existent_id) is False

    assert node_service.hard_delete_node(non_existent_id) is False


def test_get_nodes_query(db, test_node):
    """Test getting nodes query object."""

    select_stmt = NodeService(db).get_nodes_query()
    nodes = db.execute(select_stmt).scalars().all()

    assert len(nodes) >= 1
    assert any(n.id == test_node.id for n in nodes)
