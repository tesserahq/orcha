from uuid import uuid4
from app.services.workflow_version_service import WorkflowVersionService
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService


def test_list_workflows(client):
    """Test GET /workflows endpoint."""
    response = client.get("/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_create_workflow(client):
    """Test POST /workflows endpoint creates workflow with initial version."""
    response = client.post(
        "/workflows",
        json={
            "name": "Test Workflow",
            "description": "Test description",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    workflow = response.json()
    assert workflow["name"] == "Test Workflow"
    assert workflow["description"] == "Test description"
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


def test_update_workflow_with_nodes_auto_edges_router(client, db, test_workflow):
    update_data = {
        "name": "WF with graph via router",
        "nodes": [
            {
                "name": "RNode 1",
                "description": "Router node 1",
                "kind": "action",
                "settings": {"a": 1},
                "ui_settings": {"x": 10},
            },
            {
                "name": "RNode 2",
                "description": "Router node 2",
                "kind": "condition",
                "settings": {"b": 2},
                "ui_settings": {"x": 20},
            },
        ],
    }

    resp = client.put(f"/workflows/{test_workflow.id}", json=update_data)
    assert resp.status_code == 200
    workflow = resp.json()
    assert workflow["name"] == update_data["name"]

    # Verify nodes and auto edge exist for the new active version
    wv_service = WorkflowVersionService(db)
    node_service = NodeService(db)
    edge_service = EdgeService(db)

    version_obj = wv_service.get_workflow_version(workflow["active_version_id"])
    nodes = node_service.get_nodes_by_workflow_version(version_obj.id)
    edges = edge_service.get_edges_by_workflow_version(version_obj.id)

    node_names = {n.name for n in nodes}
    assert node_names == {"RNode 1", "RNode 2"}
    assert len(edges) == 1

    nodes_by_name = {n.name: n for n in nodes}
    created_edge = edges[0]
    assert created_edge.source_node_id == nodes_by_name["RNode 1"].id
    assert created_edge.target_node_id == nodes_by_name["RNode 2"].id


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


def test_get_workflow_returns_nodes_in_order(client, db, test_workflow):
    # First update with nodes to ensure nodes exist for active version
    update_data = {
        "name": "WF order check",
        "nodes": [
            {
                "name": "OrderNode 1",
                "description": "First",
                "kind": "action",
                "settings": {"a": 1},
                "ui_settings": {"x": 1},
            },
            {
                "name": "OrderNode 2",
                "description": "Second",
                "kind": "condition",
                "settings": {"b": 2},
                "ui_settings": {"x": 2},
            },
            {
                "name": "OrderNode 3",
                "description": "Third",
                "kind": "action",
                "settings": {"c": 3},
                "ui_settings": {"x": 3},
            },
        ],
    }
    put_resp = client.put(f"/workflows/{test_workflow.id}", json=update_data)
    assert put_resp.status_code == 200

    # Fetch workflow and assert nodes are present in correct order
    get_resp = client.get(f"/workflows/{test_workflow.id}")
    assert get_resp.status_code == 200
    wf = get_resp.json()
    assert "nodes" in wf
    names_in_order = [n["name"] for n in wf["nodes"]]
    assert names_in_order == ["OrderNode 1", "OrderNode 2", "OrderNode 3"]
