import pytest
from uuid import uuid4
from sqlalchemy.orm import Session
from app.schemas.event import EventCreate, EventUpdate
from app.services.event_service import EventService
from datetime import datetime, UTC


@pytest.fixture
def sample_event_data():
    return {
        "event_data": {"message": "Test event", "value": 42},
        "event_type": "test.event",
        "spec_version": "1.0",
        "time": datetime.now(UTC),
        "data_content_type": "application/json",
        "subject": "Test event",
        "tags": ["test", "event"],
        "labels": {"environment": "test"},
        "privy": False,
        "user_id": None,
        "source": "test.source",
    }


def test_create_event(db, sample_event_data):
    """Test creating a new event."""
    # Create event
    event_create = EventCreate(**sample_event_data)
    event = EventService(db).create_event(event_create)

    # Assertions
    assert event.id is not None
    assert event.event_data == sample_event_data["event_data"]
    assert event.event_type == sample_event_data["event_type"]
    assert event.spec_version == sample_event_data["spec_version"]
    assert event.created_at is not None
    assert event.updated_at is not None


def test_get_event(db, setup_event):
    """Test retrieving an event by ID."""
    # Get event
    retrieved_event = EventService(db).get_event(setup_event.id)

    # Assertions
    assert retrieved_event is not None
    assert retrieved_event.id == setup_event.id
    assert retrieved_event.event_type == setup_event.event_type


def test_get_events(db, setup_event):
    """Test retrieving all events."""
    # Get all events
    events = EventService(db).get_events()

    # Assertions
    assert len(events) >= 1
    assert any(e.id == setup_event.id for e in events)


def test_get_events_by_type(db, setup_event):
    """Test retrieving events by type."""
    # Get events by type
    events = EventService(db).get_events_by_type(setup_event.event_type)

    # Assertions
    assert len(events) >= 1
    assert any(e.id == setup_event.id for e in events)
    assert all(e.event_type == setup_event.event_type for e in events)


def test_update_event(db, setup_event):
    """Test updating an event."""
    # Update data
    update_data = {
        "event_data": {"message": "Updated event", "value": 100},
        "event_type": "updated.event",
    }
    event_update = EventUpdate(**update_data)

    # Update event
    updated_event = EventService(db).update_event(setup_event.id, event_update)

    # Assertions
    assert updated_event is not None
    assert updated_event.id == setup_event.id
    assert updated_event.event_data == update_data["event_data"]
    assert updated_event.event_type == update_data["event_type"]
    # Other fields should remain unchanged


def test_delete_event(db, setup_event):
    """Test soft deleting an event."""
    event_service = EventService(db)
    # Delete event
    success = event_service.delete_event(setup_event.id)

    # Assertions
    assert success is True
    deleted_event = event_service.get_event(setup_event.id)
    assert deleted_event is None  # Soft delete should hide it from regular queries


def test_get_deleted_event(db, setup_event):
    """Test retrieving a soft-deleted event."""
    event_service = EventService(db)
    # Delete event
    event_service.delete_event(setup_event.id)

    # Get deleted event
    deleted_event = event_service.get_deleted_event(setup_event.id)

    # Assertions
    assert deleted_event is not None
    assert deleted_event.id == setup_event.id
    assert deleted_event.deleted_at is not None


def test_restore_event(db, setup_event):
    """Test restoring a soft-deleted event."""
    event_service = EventService(db)
    # Delete event
    event_service.delete_event(setup_event.id)

    # Verify it's deleted
    assert event_service.get_event(setup_event.id) is None

    # Restore event
    success = event_service.restore_event(setup_event.id)

    # Assertions
    assert success is True
    restored_event = event_service.get_event(setup_event.id)
    assert restored_event is not None
    assert restored_event.id == setup_event.id


def test_hard_delete_event(db, setup_event):
    """Test permanently deleting an event."""
    event_service = EventService(db)
    event_id = setup_event.id

    # Hard delete event
    success = event_service.hard_delete_event(event_id)

    # Assertions
    assert success is True
    # Should not exist even when querying deleted records
    deleted_event = event_service.get_deleted_event(event_id)
    assert deleted_event is None


def test_get_deleted_events(db, setup_event):
    """Test retrieving all soft-deleted events."""
    event_service = EventService(db)
    # Delete event
    event_service.delete_event(setup_event.id)

    # Get deleted events
    deleted_events = event_service.get_deleted_events()

    # Assertions
    assert len(deleted_events) >= 1
    assert any(e.id == setup_event.id for e in deleted_events)


def test_search_events_with_filters(db, setup_event):
    """Test searching events with filters."""
    # Search using exact match on event_type
    filters = {"event_type": setup_event.event_type}
    results = EventService(db).search(filters)

    assert len(results) >= 1
    assert any(event.id == setup_event.id for event in results)

    # Search using ilike filter on event_type
    filters = {
        "event_type": {"operator": "ilike", "value": f"%{setup_event.event_type}%"}
    }
    results = EventService(db).search(filters)

    assert len(results) >= 1
    assert any(event.id == setup_event.id for event in results)

    # Search with no match
    filters = {"event_type": "nonexistent.event.type"}
    results = EventService(db).search(filters)

    assert len(results) == 0


def setup_event_not_found_cases(db):
    """Test various not found cases."""
    event_service = EventService(db)
    non_existent_id = uuid4()

    # Get non-existent event
    assert event_service.get_event(non_existent_id) is None

    # Update non-existent event
    update_data = {"event_type": "updated.event"}
    event_update = EventUpdate(**update_data)
    assert event_service.update_event(non_existent_id, event_update) is None

    # Delete non-existent event
    assert event_service.delete_event(non_existent_id) is False

    # Restore non-existent event
    assert event_service.restore_event(non_existent_id) is False

    # Hard delete non-existent event
    assert event_service.hard_delete_event(non_existent_id) is False


def test_create_event_with_default_spec_version(db):
    """Test creating an event with default spec_version."""
    event_data = {
        "event_data": {"message": "Test"},
        "event_type": "test.event",
        "time": datetime.now(UTC),
        "spec_version": "1.0",
        "data_content_type": "application/json",
        "subject": "Test event",
        "tags": ["test", "event"],
        "labels": {"environment": "test"},
        "privy": False,
        "user_id": None,
        "source": "test.source",
    }
    event_create = EventCreate(**event_data)
    event = EventService(db).create_event(event_create)

    # Assertions
    assert event.spec_version == "1.0"  # Should use default


def test_get_events_query(db, setup_event):
    """Test getting events query object."""
    select_stmt = EventService(db).get_events_query()
    events = db.execute(select_stmt).scalars().all()

    # Assertions
    assert len(events) >= 1
    assert any(e.id == setup_event.id for e in events)
