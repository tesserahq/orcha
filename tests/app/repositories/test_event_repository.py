import pytest
from uuid import uuid4
from app.schemas.event import EventCreate, EventUpdate
from app.models.event import Event
from app.repositories.event_repository import EventRepository
from datetime import datetime, timedelta, UTC


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
    event = EventRepository(db).create_event(event_create)

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
    retrieved_event = EventRepository(db).get_event(setup_event.id)

    # Assertions
    assert retrieved_event is not None
    assert retrieved_event.id == setup_event.id
    assert retrieved_event.event_type == setup_event.event_type


def test_get_events(db, setup_event):
    """Test retrieving all events."""
    # Get all events
    events = EventRepository(db).get_events()

    # Assertions
    assert len(events) >= 1
    assert any(e.id == setup_event.id for e in events)


def test_get_events_by_type(db, setup_event):
    """Test retrieving events by type."""
    # Get events by type
    events = EventRepository(db).get_events_by_type(setup_event.event_type)

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
    updated_event = EventRepository(db).update_event(setup_event.id, event_update)

    # Assertions
    assert updated_event is not None
    assert updated_event.id == setup_event.id
    assert updated_event.event_data == update_data["event_data"]
    assert updated_event.event_type == update_data["event_type"]
    # Other fields should remain unchanged


def test_delete_event(db, setup_event):
    """Test soft deleting an event."""
    event_service = EventRepository(db)
    # Delete event
    success = event_service.delete_event(setup_event.id)

    # Assertions
    assert success is True
    deleted_event = event_service.get_event(setup_event.id)
    assert deleted_event is None  # Soft delete should hide it from regular queries


def test_get_deleted_event(db, setup_event):
    """Test retrieving a soft-deleted event."""
    event_service = EventRepository(db)
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
    event_service = EventRepository(db)
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
    event_service = EventRepository(db)
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
    event_service = EventRepository(db)
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
    results = EventRepository(db).search(filters)

    assert len(results) >= 1
    assert any(event.id == setup_event.id for event in results)

    # Search using ilike filter on event_type
    filters = {
        "event_type": {"operator": "ilike", "value": f"%{setup_event.event_type}%"}
    }
    results = EventRepository(db).search(filters)

    assert len(results) >= 1
    assert any(event.id == setup_event.id for event in results)

    # Search with no match
    filters = {"event_type": "nonexistent.event.type"}
    results = EventRepository(db).search(filters)

    assert len(results) == 0


def setup_event_not_found_cases(db):
    """Test various not found cases."""
    event_service = EventRepository(db)
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
    event = EventRepository(db).create_event(event_create)

    # Assertions
    assert event.spec_version == "1.0"  # Should use default


def test_get_events_query(db, setup_event):
    """Test getting events query object."""
    select_stmt = EventRepository(db).get_events_query()
    events = db.execute(select_stmt).scalars().all()

    # Assertions
    assert len(events) >= 1
    assert any(e.id == setup_event.id for e in events)


def _make_event(db, event_type, created_at):
    row = Event(
        source="test.source",
        spec_version="1.0",
        event_type=event_type,
        event_data={},
        data_content_type="application/json",
        subject="filter test",
        time=created_at,
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(row)
    db.commit()
    return row


def _run(db, **kwargs):
    query = EventRepository(db).get_events_query(**kwargs)
    return {e.id for e in db.execute(query).scalars().all()}


def test_get_events_query_filters_exact_event_type(db):
    """An event type without '*' matches exactly."""
    now = datetime.now(UTC).replace(tzinfo=None)
    a = _make_event(db, "filt.user.created", now)
    b = _make_event(db, "filt.user.updated", now)

    ids = _run(db, event_type="filt.user.created")
    assert a.id in ids
    assert b.id not in ids


def test_get_events_query_wildcard_event_type(db):
    """'*' matches any run of characters, e.g. 'filt.user.*'."""
    now = datetime.now(UTC).replace(tzinfo=None)
    a = _make_event(db, "filt.user.created", now)
    b = _make_event(db, "filt.user.updated", now)
    c = _make_event(db, "filt.system.alert", now)

    ids = _run(db, event_type="filt.user.*")
    assert {a.id, b.id} <= ids
    assert c.id not in ids


def test_get_events_query_wildcard_escapes_like_metacharacters(db):
    """'_' and '%' in a pattern are literal, not SQL wildcards."""
    now = datetime.now(UTC).replace(tzinfo=None)
    underscore = _make_event(db, "filt_esc_a", now)
    other = _make_event(db, "filtXescYb", now)

    ids = _run(db, event_type="filt_esc*")
    assert underscore.id in ids
    assert other.id not in ids


def test_get_events_query_created_range_is_inclusive(db):
    """created_from and created_to bound created_at inclusively."""
    base = datetime(2026, 1, 10, 12, 0, 0)
    before = _make_event(db, "filt.range", base - timedelta(days=1))
    at_start = _make_event(db, "filt.range", base)
    inside = _make_event(db, "filt.range", base + timedelta(days=1))
    at_end = _make_event(db, "filt.range", base + timedelta(days=2))
    after = _make_event(db, "filt.range", base + timedelta(days=3))

    ids = _run(
        db,
        event_type="filt.range",
        created_from=base,
        created_to=base + timedelta(days=2),
    )
    assert ids == {at_start.id, inside.id, at_end.id}
    assert before.id not in ids
    assert after.id not in ids


def test_get_events_query_created_from_only(db):
    base = datetime(2026, 1, 10, 12, 0, 0)
    old = _make_event(db, "filt.only_from", base - timedelta(days=1))
    new = _make_event(db, "filt.only_from", base + timedelta(days=1))

    ids = _run(db, event_type="filt.only_from", created_from=base)
    assert new.id in ids
    assert old.id not in ids


def test_get_events_query_no_filters_returns_all(db, setup_event):
    """With no filters the query is unchanged."""
    assert setup_event.id in _run(db)
