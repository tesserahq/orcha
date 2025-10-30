from app.constants.node_kinds import NODE_KINDS, CATEGORY_FLOW


def test_list_node_kinds(client):
    resp = client.get("/nodes/kinds")
    assert resp.status_code == 200
    body = resp.json()

    # Response is wrapped in {"data": [...]}
    assert isinstance(body, dict)
    assert "data" in body
    data = body["data"]
    assert isinstance(data, list)
    assert len(data) == len(NODE_KINDS)

    # Validate a couple of well-known kinds are present
    ids = {k["id"] for k in data}
    assert "orcha-nodes.base.event_received" in ids
    assert "orcha-nodes.base.http_request" in ids

    # Validate category normalization via constants
    flow_items = [k for k in data if k["category"] == CATEGORY_FLOW]
    assert len(flow_items) >= 1
