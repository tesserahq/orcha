"""Command for creating a workflow with an initial workflow version."""

from uuid import UUID
from typing import Optional
from app.schemas.workflow import Workflow, WorkflowCreate
from app.schemas.workflow_version import WorkflowVersionCreate
from app.repositories.workflow_version_repository import WorkflowVersionRepository
from app.commands.workflow.workflow_command_base import WorkflowCommandBase


class CreateWorkflowCommand(WorkflowCommandBase):
    def execute(
        self, workflow_data: WorkflowCreate, user_id: Optional[UUID] = None
    ) -> Workflow:
        """Create a new workflow with its initial version and optional nodes."""
        # Create the workflow using the service
        workflow = self.workflow_repository.create_workflow(
            workflow_data, created_by_id=user_id
        )

        # Create the initial workflow version with the same active status as the workflow
        workflow_version_service = WorkflowVersionRepository(self.db)
        version_data = WorkflowVersionCreate(
            workflow_id=workflow.id,
            version=1,
            is_active=workflow_data.is_active,
        )
        workflow_version = workflow_version_service.create_workflow_version(
            version_data
        )

        # Create nodes and edges if provided
        self.create_nodes_and_edges(workflow_version.id, workflow_data.nodes)

        # Set the initial version as the active version (deactivates previous active versions)
        workflow = self.workflow_repository.set_active_version(
            workflow.id, workflow_version.id
        )

        return workflow
