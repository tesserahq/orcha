from uuid import uuid4


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


def _add_event(db, event_type, created_at):
    from app.models.event import Event

    event = Event(
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
    db.add(event)
    db.commit()
    return event


def _ids(response):
    return {item["id"] for item in response.json()["items"]}


def test_list_events_filter_by_wildcard_event_type(client, db):
    """GET /events?event_type=prefix.* returns only matching types."""
    from datetime import datetime

    now = datetime(2026, 1, 10, 12, 0, 0)
    match_a = _add_event(db, "rtest.user.created", now)
    match_b = _add_event(db, "rtest.user.updated", now)
    other = _add_event(db, "rtest.system.alert", now)

    response = client.get("/events", params={"event_type": "rtest.user.*"})
    assert response.status_code == 200
    ids = _ids(response)
    assert {str(match_a.id), str(match_b.id)} <= ids
    assert str(other.id) not in ids


def test_list_events_filter_by_exact_event_type(client, db):
    from datetime import datetime

    now = datetime(2026, 1, 10, 12, 0, 0)
    exact = _add_event(db, "rtest.exact", now)
    _add_event(db, "rtest.exact.more", now)

    response = client.get("/events", params={"event_type": "rtest.exact"})
    assert response.status_code == 200
    assert _ids(response) == {str(exact.id)}


def test_list_events_filter_by_created_range(client, db):
    """created_from / created_to bound created_at inclusively."""
    from datetime import datetime, timedelta

    base = datetime(2026, 2, 1, 0, 0, 0)
    before = _add_event(db, "rtest.range", base - timedelta(days=1))
    inside = _add_event(db, "rtest.range", base + timedelta(days=1))
    after = _add_event(db, "rtest.range", base + timedelta(days=5))

    response = client.get(
        "/events",
        params={
            "event_type": "rtest.range",
            "created_from": base.isoformat(),
            "created_to": (base + timedelta(days=2)).isoformat(),
        },
    )
    assert response.status_code == 200
    ids = _ids(response)
    assert str(inside.id) in ids
    assert str(before.id) not in ids
    assert str(after.id) not in ids


def test_list_events_created_range_accepts_timezone_aware_values(client, db):
    """Offsets are normalized to UTC so they compare against stored naive UTC."""
    from datetime import datetime

    created = datetime(2026, 3, 1, 12, 0, 0)
    event = _add_event(db, "rtest.tz", created)

    # 14:00 at +02:00 is 12:00 UTC, so the boundary is inclusive.
    response = client.get(
        "/events",
        params={
            "event_type": "rtest.tz",
            "created_from": "2026-03-01T14:00:00+02:00",
        },
    )
    assert response.status_code == 200
    assert str(event.id) in _ids(response)


def test_list_events_rejects_inverted_created_range(client):
    response = client.get(
        "/events",
        params={
            "created_from": "2026-03-02T00:00:00",
            "created_to": "2026-03-01T00:00:00",
        },
    )
    assert response.status_code == 400
    assert "created_from" in response.json()["detail"]
