"""Command for updating an existing workflow."""

from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.workflow import Workflow, WorkflowUpdate, WorkflowUpdateRequest
from app.schemas.workflow_version import WorkflowVersionCreate
from app.services.workflow_service import WorkflowService
from app.services.workflow_version_service import WorkflowVersionService
from app.schemas.node import NodeCreate, NodeCreatePayload
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService
from app.schemas.edge import EdgeCreate


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
            node_data = NodeCreate(
                name=node_payload.name,
                description=node_payload.description,
                kind=node_payload.kind,
                settings=node_payload.settings,
                ui_settings=node_payload.ui_settings,
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

    def set_active_version(self, workflow_id: UUID, version_id: UUID) -> Workflow:
        """Set the active version for a workflow."""
        return self.workflow_service.update_workflow(
            workflow_id, WorkflowUpdate(active_version_id=version_id)
        )


class UpdateWorkflowCommand(WorkflowCommandBase):
    def execute(
        self, workflow_id: UUID, workflow_data: WorkflowUpdateRequest
    ) -> Workflow:
        """Update an existing workflow and return the updated entity."""
        workflow = self.workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise Exception(f"Workflow with id {workflow_id} not found")

        updated_workflow = self.workflow_service.update_workflow(
            workflow_id, workflow_data
        )

        workflow_version = self.create_new_version(updated_workflow)

        # Create nodes and edges if provided
        self.create_nodes_and_edges(workflow_version.id, workflow_data.nodes)

        # Set the new version as the active version
        updated_workflow = self.set_active_version(workflow.id, workflow_version.id)

        return updated_workflow

    def create_new_version(self, workflow: Workflow):
        workflow_version_service = WorkflowVersionService(self.db)
        workflow_version = workflow_version_service.create_workflow_version(
            WorkflowVersionCreate(
                workflow_id=workflow.id,
                version=workflow_version_service.get_next_version(workflow.id),
                is_active=workflow.is_active,
            )
        )

        return workflow_version
