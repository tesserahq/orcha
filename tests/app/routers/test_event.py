from uuid import uuid4
from datetime import datetime, UTC


def test_list_events(client):
    """Test GET /events endpoint."""
    response = client.get("/events")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_create_event(client, test_source):
    """Test POST /events endpoint."""
    response = client.post(
        "/events",
        json={
            "data": {"message": "Test event", "value": 42},
            "event_type": "test.event",
            "spec_version": "1.0",
            "time": datetime.now(UTC).isoformat(),
            "source_id": str(test_source.id),
        },
    )
    assert response.status_code == 201
    event = response.json()
    assert event["event_type"] == "test.event"
    assert event["data"]["message"] == "Test event"
    assert event["source_id"] == str(test_source.id)
    assert "id" in event
    assert "created_at" in event
    assert "updated_at" in event


def test_get_event(client, test_event):
    """Test GET /events/{id} endpoint."""
    response = client.get(f"/events/{test_event.id}")
    assert response.status_code == 200
    event = response.json()
    assert event["id"] == str(test_event.id)
    assert event["event_type"] == test_event.event_type
    assert event["source_id"] == str(test_event.source_id)


def test_get_event_not_found(client):
    """Test GET /events/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.get(f"/events/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_update_event(client, test_event):
    """Test PUT /events/{id} endpoint."""
    update_data = {
        "data": {"message": "Updated event"},
        "event_type": "updated.event",
    }
    response = client.put(
        f"/events/{test_event.id}",
        json=update_data,
    )
    assert response.status_code == 200
    event = response.json()
    assert event["data"]["message"] == "Updated event"
    assert event["event_type"] == "updated.event"
    # Other fields should remain unchanged
    assert event["source_id"] == str(test_event.source_id)


def test_update_event_not_found(client):
    """Test PUT /events/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.put(
        f"/events/{non_existent_id}",
        json={"event_type": "updated.event"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_delete_event(client, test_event):
    """Test DELETE /events/{id} endpoint."""
    event_id = test_event.id
    response = client.delete(f"/events/{event_id}")
    assert response.status_code == 204

    # Verify it's soft deleted (should not appear in list)
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 404


def test_delete_event_not_found(client):
    """Test DELETE /events/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.delete(f"/events/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_list_events_by_source(client, test_event, test_source):
    """Test GET /events/source/{source_id} endpoint."""
    response = client.get(f"/events/source/{test_source.id}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    # Should include our test event
    assert any(e["id"] == str(test_event.id) for e in data["items"])


def test_list_events_by_source_not_found(client):
    """Test GET /events/source/{source_id} endpoint with non-existent source."""
    non_existent_id = uuid4()
    response = client.get(f"/events/source/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Source not found"


def test_list_events_by_type(client, test_event):
    """Test GET /events/type/{event_type} endpoint."""
    response = client.get(f"/events/type/{test_event.event_type}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    # Should include our test event
    assert any(e["id"] == str(test_event.id) for e in data["items"])


def test_create_event_with_invalid_source(client):
    """Test creating an event with non-existent source."""
    non_existent_source_id = uuid4()
    response = client.post(
        "/events",
        json={
            "data": {"message": "Test"},
            "event_type": "test.event",
            "time": datetime.now(UTC).isoformat(),
            "source_id": str(non_existent_source_id),
        },
    )
    assert response.status_code == 400
    assert "Source not found" in response.json()["detail"]


def test_update_event_with_invalid_source(client, test_event):
    """Test updating an event with non-existent source."""
    non_existent_source_id = uuid4()
    response = client.put(
        f"/events/{test_event.id}",
        json={"source_id": str(non_existent_source_id)},
    )
    assert response.status_code == 400
    assert "Source not found" in response.json()["detail"]


def test_create_event_minimal_data(client, test_source):
    """Test creating an event with minimal required fields."""
    response = client.post(
        "/events",
        json={
            "data": {"message": "Minimal event"},
            "event_type": "minimal.event",
            "time": datetime.now(UTC).isoformat(),
            "source_id": str(test_source.id),
        },
    )
    assert response.status_code == 201
    event = response.json()
    assert event["event_type"] == "minimal.event"
    assert event["spec_version"] == "1.0"  # Should use default
    assert event["data"]["message"] == "Minimal event"


def test_list_events_pagination(client, test_event):
    """Test pagination in GET /events endpoint."""
    # Test with pagination
    response = client.get("/events?page=1&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1

    response = client.get("/events?page=2&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1
