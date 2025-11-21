import pytest
from app.models.event import Event
from datetime import datetime, UTC, timezone


@pytest.fixture(scope="function")
def setup_event(db, faker):
    """Create a test event for use in tests."""
    event_data = {
        "source": faker.uri(),
        "spec_version": "1.0",
        "event_type": faker.random_element(
            elements=("user.created", "user.updated", "system.alert")
        ),
        "event_data": {"payload": faker.pydict(value_types=[str])},
        "data_content_type": "application/json",
        "subject": faker.sentence(nb_words=3),
        "time": faker.date_time(tzinfo=timezone.utc),
        "tags": faker.words(nb=3),
        "labels": {"environment": faker.random_element(elements=("prod", "dev", "qa"))},
    }

    event = Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@pytest.fixture(scope="function")
def setup_another_event(db, faker):
    """Create another test event for use in tests."""
    event_data = {
        "event_data": {
            "message": faker.sentence(),
            "value": faker.random_int(min=1, max=100),
        },
        "event_type": faker.word(),
        "spec_version": "1.0",
        "time": datetime.now(UTC),
    }

    event = Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)

    return event
