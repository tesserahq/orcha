from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.node import NodeCreatePayload
from app.services.workflow_service import WorkflowService
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService
from app.schemas.edge import EdgeCreate
from app.schemas.node import NodeCreate
from app.constants.node_kinds import NODE_KIND_BY_ID


class WorkflowCommandBase:
    """Base class for workflow commands with shared functionality."""

    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(self.db)

    def create_nodes_and_edges(
        self, workflow_version_id: UUID, nodes: Optional[List[NodeCreatePayload]]
    ) -> List:
        """Create nodes and auto-create edges between consecutive nodes for a workflow version."""
        if not nodes:
            return []

        node_service = NodeService(self.db)
        created_nodes = []

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
            edge_service = EdgeService(self.db)
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
