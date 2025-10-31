from app.constants.node_kinds import (
    NODE_KINDS,
    CATEGORY_FLOW,
    CATEGORY_ACTION_APP,
    NODE_CATEGORIES,
    NODE_KINDS_BY_CATEGORY,
)


def test_list_categories(client):
    resp = client.get("/nodes/categories")
    assert resp.status_code == 200
    body = resp.json()

    # Response is wrapped in {"items": [...]}
    assert isinstance(body, dict)
    assert "items" in body
    data = body["items"]
    assert isinstance(data, list)
    assert len(data) == len(NODE_CATEGORIES)

    # Validate structure: each item should have category info and nodes
    for category in data:
        assert "key" in category
        assert "name" in category
        assert "description" in category
        assert "nodes" in category
        assert isinstance(category["nodes"], list)

    # Validate that categories are present
    category_keys = {c["key"] for c in data}
    assert CATEGORY_FLOW in category_keys
    assert CATEGORY_ACTION_APP in category_keys

    # Validate a couple of well-known node kinds are present in their categories
    all_node_ids = set()
    for category in data:
        for node in category["nodes"]:
            all_node_ids.add(node["id"])

    assert "orcha-nodes.base.event_received" in all_node_ids
    assert "orcha-nodes.base.http_request" in all_node_ids

    # Validate that nodes are grouped correctly by category
    flow_category = next(c for c in data if c["key"] == CATEGORY_FLOW)
    assert len(flow_category["nodes"]) >= 1
    assert all(node["category"] == CATEGORY_FLOW for node in flow_category["nodes"])

    # Validate the total number of nodes matches
    total_nodes_in_response = sum(len(c["nodes"]) for c in data)
    assert total_nodes_in_response == len(NODE_KINDS)

    # Validate that nodes include all required fields
    date_time_node = next(
        (
            node
            for category in data
            for node in category["nodes"]
            if node["id"] == "orcha-nodes.base.date_time"
        ),
        None,
    )
    assert date_time_node is not None
    assert "displayName" in date_time_node
    assert "name" in date_time_node
    assert "icon" in date_time_node
    assert "group" in date_time_node
    assert "version" in date_time_node
    assert "subtitle" in date_time_node
    assert "description" in date_time_node
    assert "defaults" in date_time_node
    assert "inputs" in date_time_node
    assert "outputs" in date_time_node
    assert "properties" in date_time_node
    assert "category" in date_time_node
    # Validate specific values for date_time node
    assert date_time_node["displayName"] == "Date & Time"
    assert date_time_node["name"] == "dateTime"
    assert date_time_node["icon"] == "fa:clock"
    assert date_time_node["subtitle"] == "Manipulate dates"
