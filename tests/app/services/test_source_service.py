import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.source import SourceCreate, SourceUpdate
from app.services.source_service import SourceService


@pytest.fixture
def sample_source_data():
    return {
        "name": "Test Source",
        "description": "This is a test source description",
        "identifier": "test-source-001",
    }


def test_create_source(db, sample_source_data):
    """Test creating a new source."""
    # Create source
    source_create = SourceCreate(**sample_source_data)
    source = SourceService(db).create_source(source_create)

    # Assertions
    assert source.id is not None
    assert source.name == sample_source_data["name"]
    assert source.description == sample_source_data["description"]
    assert source.identifier == sample_source_data["identifier"]
    assert source.created_at is not None
    assert source.updated_at is not None


def test_get_source(db, test_source):
    """Test retrieving a source by ID."""
    # Get source
    retrieved_source = SourceService(db).get_source(test_source.id)

    # Assertions
    assert retrieved_source is not None
    assert retrieved_source.id == test_source.id
    assert retrieved_source.name == test_source.name


def test_get_source_by_identifier(db, test_source):
    """Test retrieving a source by identifier."""
    # Get source by identifier
    retrieved_source = SourceService(db).get_source_by_identifier(
        test_source.identifier
    )

    # Assertions
    assert retrieved_source is not None
    assert retrieved_source.id == test_source.id
    assert retrieved_source.identifier == test_source.identifier


def test_get_sources(db, test_source):
    """Test retrieving all sources."""
    # Get all sources
    sources = SourceService(db).get_sources()

    # Assertions
    assert len(sources) >= 1
    assert any(s.id == test_source.id for s in sources)


def test_update_source(db, test_source):
    """Test updating a source."""
    # Update data
    update_data = {
        "name": "Updated Source Name",
        "description": "Updated description",
    }
    source_update = SourceUpdate(**update_data)

    # Update source
    updated_source = SourceService(db).update_source(test_source.id, source_update)

    # Assertions
    assert updated_source is not None
    assert updated_source.id == test_source.id
    assert updated_source.name == update_data["name"]
    assert updated_source.description == update_data["description"]
    # identifier should remain unchanged as it wasn't in update_data
    assert updated_source.identifier == test_source.identifier


def test_delete_source(db, test_source):
    """Test soft deleting a source."""
    source_service = SourceService(db)
    # Delete source
    success = source_service.delete_source(test_source.id)

    # Assertions
    assert success is True
    deleted_source = source_service.get_source(test_source.id)
    assert deleted_source is None  # Soft delete should hide it from regular queries


def test_get_deleted_source(db, test_source):
    """Test retrieving a soft-deleted source."""
    source_service = SourceService(db)
    # Delete source
    source_service.delete_source(test_source.id)

    # Get deleted source
    deleted_source = source_service.get_deleted_source(test_source.id)

    # Assertions
    assert deleted_source is not None
    assert deleted_source.id == test_source.id
    assert deleted_source.deleted_at is not None


def test_restore_source(db, test_source):
    """Test restoring a soft-deleted source."""
    source_service = SourceService(db)
    # Delete source
    source_service.delete_source(test_source.id)

    # Verify it's deleted
    assert source_service.get_source(test_source.id) is None

    # Restore source
    success = source_service.restore_source(test_source.id)

    # Assertions
    assert success is True
    restored_source = source_service.get_source(test_source.id)
    assert restored_source is not None
    assert restored_source.id == test_source.id


def test_hard_delete_source(db, test_source):
    """Test permanently deleting a source."""
    source_service = SourceService(db)
    source_id = test_source.id

    # Hard delete source
    success = source_service.hard_delete_source(source_id)

    # Assertions
    assert success is True
    # Should not exist even when querying deleted records
    deleted_source = source_service.get_deleted_source(source_id)
    assert deleted_source is None


def test_get_deleted_sources(db, test_source):
    """Test retrieving all soft-deleted sources."""
    source_service = SourceService(db)
    # Delete source
    source_service.delete_source(test_source.id)

    # Get deleted sources
    deleted_sources = source_service.get_deleted_sources()

    # Assertions
    assert len(deleted_sources) >= 1
    assert any(s.id == test_source.id for s in deleted_sources)


def test_search_sources_with_filters(db, test_source):
    """Test searching sources with filters."""
    # First, let's get some actual text from the source name to search for
    source_name_part = test_source.name.split()[0] if test_source.name else ""

    # Search using ilike filter on name
    if source_name_part:
        filters = {"name": {"operator": "ilike", "value": f"%{source_name_part}%"}}
        results = SourceService(db).search(filters)

        assert isinstance(results, list)
        assert any(source.id == test_source.id for source in results)

    # Search using exact match on identifier
    filters = {"identifier": test_source.identifier}
    results = SourceService(db).search(filters)

    assert len(results) == 1
    assert results[0].id == test_source.id

    # Search with no match
    filters = {"name": {"operator": "==", "value": "nonexistent-source-name-xyz"}}
    results = SourceService(db).search(filters)

    assert len(results) == 0


def test_source_not_found_cases(db):
    """Test various not found cases."""
    source_service = SourceService(db)
    non_existent_id = uuid4()

    # Get non-existent source
    assert source_service.get_source(non_existent_id) is None

    # Get by non-existent identifier
    assert source_service.get_source_by_identifier("nonexistent-identifier") is None

    # Update non-existent source
    update_data = {"name": "Updated Name"}
    source_update = SourceUpdate(**update_data)
    assert source_service.update_source(non_existent_id, source_update) is None

    # Delete non-existent source
    assert source_service.delete_source(non_existent_id) is False

    # Restore non-existent source
    assert source_service.restore_source(non_existent_id) is False

    # Hard delete non-existent source
    assert source_service.hard_delete_source(non_existent_id) is False
