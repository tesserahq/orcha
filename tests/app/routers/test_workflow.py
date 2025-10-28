from uuid import uuid4


def test_list_workflows(client):
    """Test GET /workflows endpoint."""
    response = client.get("/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_create_workflow(client):
    """Test POST /workflows endpoint."""
    response = client.post(
        "/workflows",
        json={
            "name": "Test Workflow",
            "description": "Test description",
            "trigger_event_type": "test.event",
            "trigger_event_filters": {"field": "test", "value": "value"},
            "is_active": True,
        },
    )
    assert response.status_code == 201
    workflow = response.json()
    assert workflow["name"] == "Test Workflow"
    assert workflow["description"] == "Test description"
    assert workflow["trigger_event_type"] == "test.event"
    assert workflow["trigger_event_filters"] == {"field": "test", "value": "value"}
    assert workflow["is_active"] is True
    assert "id" in workflow
    assert "created_at" in workflow
    assert "updated_at" in workflow


def test_get_workflow(client, test_workflow):
    """Test GET /workflows/{id} endpoint."""
    response = client.get(f"/workflows/{test_workflow.id}")
    assert response.status_code == 200
    workflow = response.json()
    assert workflow["id"] == str(test_workflow.id)
    assert workflow["name"] == test_workflow.name
    assert workflow["trigger_event_type"] == test_workflow.trigger_event_type


def test_get_workflow_not_found(client):
    """Test GET /workflows/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.get(f"/workflows/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Workflow not found"


def test_update_workflow(client, test_workflow):
    """Test PUT /workflows/{id} endpoint."""
    update_data = {
        "name": "Updated Workflow Name",
        "description": "Updated description",
        "is_active": False,
    }
    response = client.put(
        f"/workflows/{test_workflow.id}",
        json=update_data,
    )
    assert response.status_code == 200
    workflow = response.json()
    assert workflow["name"] == update_data["name"]
    assert workflow["description"] == update_data["description"]
    assert workflow["is_active"] == update_data["is_active"]


def test_update_workflow_not_found(client):
    """Test PUT /workflows/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.put(
        f"/workflows/{non_existent_id}",
        json={"name": "Updated Name"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Workflow not found"


def test_delete_workflow(client, test_workflow):
    """Test DELETE /workflows/{id} endpoint."""
    workflow_id = test_workflow.id
    response = client.delete(f"/workflows/{workflow_id}")
    assert response.status_code == 204

    # Verify it's soft deleted
    response = client.get(f"/workflows/{workflow_id}")
    assert response.status_code == 404


def test_delete_workflow_not_found(client):
    """Test DELETE /workflows/{id} endpoint with non-existent ID."""
    non_existent_id = uuid4()
    response = client.delete(f"/workflows/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Workflow not found"


def test_list_workflows_pagination(client, test_workflow):
    """Test pagination in GET /workflows endpoint."""
    response = client.get("/workflows?page=1&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1

    response = client.get("/workflows?page=2&size=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 1
