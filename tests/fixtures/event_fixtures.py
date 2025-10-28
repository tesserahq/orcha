import pytest
from app.models.event import Event
from datetime import datetime, UTC


@pytest.fixture(scope="function")
def test_event(db, faker, test_source):
    """Create a test event for use in tests."""
    event_data = {
        "data": {
            "message": faker.sentence(),
            "value": faker.random_int(min=1, max=100),
        },
        "event_type": faker.word(),
        "spec_version": "1.0",
        "time": datetime.now(UTC),
        "source_id": test_source.id,
    }

    event = Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@pytest.fixture(scope="function")
def setup_event(db, faker, setup_source):
    """Create a test event for use in tests."""
    event_data = {
        "data": {
            "message": faker.sentence(),
            "value": faker.random_int(min=1, max=100),
        },
        "event_type": faker.word(),
        "spec_version": "1.0",
        "time": datetime.now(UTC),
        "source_id": setup_source.id,
    }

    event = Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@pytest.fixture(scope="function")
def setup_another_event(db, faker, setup_source):
    """Create another test event for use in tests."""
    event_data = {
        "data": {
            "message": faker.sentence(),
            "value": faker.random_int(min=1, max=100),
        },
        "event_type": faker.word(),
        "spec_version": "1.0",
        "time": datetime.now(UTC),
        "source_id": setup_source.id,
    }

    event = Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)

    return event
