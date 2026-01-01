from uuid import uuid4
from datetime import datetime, UTC


def test_list_events(client):
    """Test GET /events endpoint."""
    response = client.get("/events")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_event(client, setup_event):
    """Test GET /events/{id} endpoint."""
    response = client.get(f"/events/{setup_event.id}")
    assert response.status_code == 200
    event = response.json()
    assert event["id"] == str(setup_event.id)
    assert event["event_type"] == setup_event.event_type
    assert event["source"] == setup_event.source


def test_get_event_not_found(client):
    """Test GET /events/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.get(f"/events/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_delete_event(client, setup_event):
    """Test DELETE /events/{id} endpoint."""
    event_id = setup_event.id
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


def test_list_events_pagination(client, setup_event):
    """Test pagination in GET /events endpoint."""
    # Test with pagination
    response = client.get("/events?page=1&size=1")
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1

    response = client.get("/events?page=2&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1
