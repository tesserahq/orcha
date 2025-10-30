import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.edge import EdgeCreate, EdgeUpdate
from app.services.edge_service import EdgeService


@pytest.fixture
def sample_edge_data(test_node, setup_node):
    return {
        "name": "Test Edge",
        "source_node_id": test_node.id,
        "target_node_id": setup_node.id,
        "workflow_version_id": test_node.workflow_version_id,
        "settings": {"key": "value"},
        "ui_settings": {"type": "bezier"},
    }


def test_create_edge(db: Session, sample_edge_data):
    """Test creating a new edge."""
    edge_create = EdgeCreate(**sample_edge_data)
    edge = EdgeService(db).create_edge(edge_create)

    assert edge.id is not None
    assert edge.name == sample_edge_data["name"]
    assert edge.source_node_id == sample_edge_data["source_node_id"]
    assert edge.target_node_id == sample_edge_data["target_node_id"]
    assert edge.workflow_version_id == sample_edge_data["workflow_version_id"]
    assert edge.settings == sample_edge_data["settings"]
    assert edge.ui_settings == sample_edge_data["ui_settings"]
    assert edge.created_at is not None
    assert edge.updated_at is not None


def test_get_edge(db: Session, test_edge):
    """Test retrieving an edge by ID."""
    retrieved_edge = EdgeService(db).get_edge(test_edge.id)

    assert retrieved_edge is not None
    assert retrieved_edge.id == test_edge.id
    assert retrieved_edge.name == test_edge.name


def test_get_edges(db: Session, test_edge):
    """Test retrieving all edges."""
    edges = EdgeService(db).get_edges()

    assert len(edges) >= 1
    assert any(e.id == test_edge.id for e in edges)


def test_get_edges_by_workflow_version(db: Session, test_edge):
    """Test retrieving edges by workflow version."""
    edges = EdgeService(db).get_edges_by_workflow_version(test_edge.workflow_version_id)

    assert len(edges) >= 1
    assert any(e.id == test_edge.id for e in edges)
    assert all(e.workflow_version_id == test_edge.workflow_version_id for e in edges)


def test_get_edges_by_source_node(db: Session, test_edge):
    """Test retrieving edges by source node."""
    edges = EdgeService(db).get_edges_by_source_node(test_edge.source_node_id)

    assert len(edges) >= 1
    assert any(e.id == test_edge.id for e in edges)
    assert all(e.source_node_id == test_edge.source_node_id for e in edges)


def test_get_edges_by_target_node(db: Session, test_edge):
    """Test retrieving edges by target node."""
    edges = EdgeService(db).get_edges_by_target_node(test_edge.target_node_id)

    assert len(edges) >= 1
    assert any(e.id == test_edge.id for e in edges)
    assert all(e.target_node_id == test_edge.target_node_id for e in edges)


def test_get_edges_by_node(db: Session, test_edge):
    """Test retrieving edges connected to a node (source or target)."""
    edges_as_source = EdgeService(db).get_edges_by_node(test_edge.source_node_id)
    edges_as_target = EdgeService(db).get_edges_by_node(test_edge.target_node_id)

    assert len(edges_as_source) >= 1
    assert any(e.id == test_edge.id for e in edges_as_source)

    assert len(edges_as_target) >= 1
    assert any(e.id == test_edge.id for e in edges_as_target)


def test_update_edge(db: Session, test_edge):
    """Test updating an edge."""
    update_data = {
        "name": "Updated Edge Name",
        "settings": {"key": "updated_value"},
    }
    edge_update = EdgeUpdate(**update_data)

    updated_edge = EdgeService(db).update_edge(test_edge.id, edge_update)

    assert updated_edge is not None
    assert updated_edge.id == test_edge.id
    assert updated_edge.name == update_data["name"]
    assert updated_edge.settings == update_data["settings"]


def test_delete_edge(db: Session, test_edge):
    """Test soft deleting an edge."""
    edge_service = EdgeService(db)
    success = edge_service.delete_edge(test_edge.id)

    assert success is True
    deleted_edge = edge_service.get_edge(test_edge.id)
    assert deleted_edge is None


def test_get_deleted_edge(db: Session, test_edge):
    """Test retrieving a soft-deleted edge."""
    edge_service = EdgeService(db)
    edge_service.delete_edge(test_edge.id)

    deleted_edge = edge_service.get_deleted_edge(test_edge.id)

    assert deleted_edge is not None
    assert deleted_edge.id == test_edge.id
    assert deleted_edge.deleted_at is not None


def test_restore_edge(db: Session, test_edge):
    """Test restoring a soft-deleted edge."""
    edge_service = EdgeService(db)
    edge_service.delete_edge(test_edge.id)

    assert edge_service.get_edge(test_edge.id) is None

    success = edge_service.restore_edge(test_edge.id)

    assert success is True
    restored_edge = edge_service.get_edge(test_edge.id)
    assert restored_edge is not None
    assert restored_edge.id == test_edge.id


def test_hard_delete_edge(db: Session, test_edge):
    """Test permanently deleting an edge."""
    edge_service = EdgeService(db)
    edge_id = test_edge.id

    success = edge_service.hard_delete_edge(edge_id)

    assert success is True
    deleted_edge = edge_service.get_deleted_edge(edge_id)
    assert deleted_edge is None


def test_get_deleted_edges(db: Session, test_edge):
    """Test retrieving all soft-deleted edges."""
    edge_service = EdgeService(db)
    edge_service.delete_edge(test_edge.id)

    deleted_edges = edge_service.get_deleted_edges()

    assert len(deleted_edges) >= 1
    assert any(e.id == test_edge.id for e in deleted_edges)


def test_search_edges_with_filters(db: Session, test_edge):
    """Test searching edges with filters."""
    filters = {"name": {"operator": "ilike", "value": f"%{test_edge.name}%"}}
    results = EdgeService(db).search(filters)

    assert isinstance(results, list)
    assert any(edge.id == test_edge.id for edge in results)

    filters = {"source_node_id": test_edge.source_node_id}
    results = EdgeService(db).search(filters)

    assert len(results) >= 1
    assert results[0].id == test_edge.id


def test_edge_not_found_cases(db: Session):
    """Test various not found cases."""
    edge_service = EdgeService(db)
    non_existent_id = uuid4()

    assert edge_service.get_edge(non_existent_id) is None

    update_data = {"name": "Updated Name"}
    edge_update = EdgeUpdate(**update_data)
    assert edge_service.update_edge(non_existent_id, edge_update) is None

    assert edge_service.delete_edge(non_existent_id) is False

    assert edge_service.restore_edge(non_existent_id) is False

    assert edge_service.hard_delete_edge(non_existent_id) is False


def test_get_edges_query(db: Session, test_edge):
    """Test getting edges query object."""

    select_stmt = EdgeService(db).get_edges_query()
    edges = db.execute(select_stmt).scalars().all()

    assert len(edges) >= 1
    assert any(e.id == test_edge.id for e in edges)
