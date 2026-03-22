from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.node import NodeCreatePayload
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.node_repository import NodeRepository
from app.repositories.edge_repository import EdgeRepository
from app.schemas.edge import EdgeCreate
from app.schemas.node import NodeCreate
from app.constants.node_categories import CATEGORY_TRIGGER
from app.constants.node_kinds import NODE_BY_ID, NODE_KIND_BY_ID


class WorkflowCommandBase:
    """Base class for workflow commands with shared functionality."""

    def __init__(self, db: Session):
        self.db = db
        self.workflow_repository = WorkflowRepository(self.db)

    def create_nodes_and_edges(
        self, workflow_version_id: UUID, nodes: Optional[List[NodeCreatePayload]]
    ) -> List:
        """Create nodes and auto-create edges between consecutive nodes for a workflow version."""
        if not nodes:
            return []

        node_service = NodeRepository(self.db)
        created_nodes = []

        trigger_count = sum(
            1
            for n in nodes
            if NODE_BY_ID.get(n.kind)
            and NODE_BY_ID[n.kind].category == CATEGORY_TRIGGER
        )
        if trigger_count == 0:
            raise ValueError("Workflow must have exactly one trigger node, found none")
        if trigger_count > 1:
            raise ValueError(
                f"Workflow must have exactly one trigger node, found {trigger_count}"
            )

        for node_payload in nodes:
            # Validate that the node kind is valid
            if node_payload.kind not in NODE_KIND_BY_ID:
                raise ValueError(f"Invalid node kind: {node_payload.kind}")

            node_data = NodeCreate(
                name=node_payload.name,
                description=node_payload.description,
                kind=node_payload.kind,
                properties=node_payload.properties,
                ui_settings=node_payload.ui_settings,
                parameters=node_payload.parameters,
                workflow_version_id=workflow_version_id,
            )
            created_node = node_service.create_node(node_data)
            created_nodes.append(created_node)

        # Auto-create edges based on node order (consecutive pairs)
        if len(created_nodes) >= 2:
            edge_service = EdgeRepository(self.db)
            for i in range(len(created_nodes) - 1):
                src = created_nodes[i]
                tgt = created_nodes[i + 1]
                edge_data = EdgeCreate(
                    name=None,
                    source_node_id=src.id,
                    target_node_id=tgt.id,
                    workflow_version_id=workflow_version_id,
                    settings={},
                    ui_settings={},
                )
                edge_service.create_edge(edge_data)

        return created_nodes
