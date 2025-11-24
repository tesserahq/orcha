from app.commands.workflow import UpdateWorkflowCommand
from app.schemas.workflow import WorkflowUpdateRequest
from app.schemas.node import NodeCreatePayload
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService
from app.services.workflow_version_service import WorkflowVersionService


def test_update_workflow_command_updates_fields(db, test_workflow):
    command = UpdateWorkflowCommand(db)
    payload = WorkflowUpdateRequest(
        name="Updated Workflow Name",
        description="Updated description",
        is_active=False,
    )

    updated = command.execute(test_workflow.id, payload)

    assert updated is not None
    assert updated.id == test_workflow.id
    assert updated.name == payload.name
    assert updated.description == payload.description
    assert updated.is_active is False


def test_update_workflow_with_nodes_auto_edges(db, test_workflow):
    command = UpdateWorkflowCommand(db)
    node1 = NodeCreatePayload(
        name="Node 1",
        description="Test node 1",
        kind="orcha-nodes.base.http_request",
        properties=[{"a": 1}],
        ui_settings={"x": 1},
    )
    node2 = NodeCreatePayload(
        name="Node 2",
        description="Test node 2",
        kind="orcha-nodes.base.if",
        properties=[{"b": 2}],
        ui_settings={"x": 2},
    )
    payload = WorkflowUpdateRequest(
        name="Workflow w/ graph",
        nodes=[node1, node2],
    )

    updated = command.execute(test_workflow.id, payload)
    assert updated is not None
    assert updated.name == "Workflow w/ graph"

    # Check new version has nodes and edges
    workflow_version_service = WorkflowVersionService(db)
    node_service = NodeService(db)
    edge_service = EdgeService(db)
    version_obj = workflow_version_service.get_workflow_version(
        updated.active_version_id
    )
    all_nodes = node_service.get_nodes_by_workflow_version(version_obj.id)
    all_edges = edge_service.get_edges_by_workflow_version(version_obj.id)

    node_names = {n.name for n in all_nodes}
    assert len(all_edges) == 1
    # Ensure the edge connects Node 1 -> Node 2
    nodes_by_name = {n.name: n for n in all_nodes}
    created_edge = all_edges[0]
    assert created_edge.source_node_id == nodes_by_name["Node 1"].id
    assert created_edge.target_node_id == nodes_by_name["Node 2"].id
