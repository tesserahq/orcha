"""Command for updating an existing workflow."""

from uuid import UUID
from app.schemas.workflow import Workflow, WorkflowUpdateRequest
from app.schemas.workflow_version import WorkflowVersionCreate
from app.services.workflow_version_service import WorkflowVersionService
from app.commands.workflow.workflow_command_base import WorkflowCommandBase


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

        # Set the new version as the active version (deactivates previous active versions)
        updated_workflow = self.workflow_service.set_active_version(
            workflow.id, workflow_version.id
        )

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
