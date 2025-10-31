"""Command for creating a workflow with an initial workflow version."""

from app.schemas.workflow import Workflow, WorkflowCreate
from app.schemas.workflow_version import WorkflowVersionCreate
from app.services.workflow_version_service import WorkflowVersionService
from app.commands.update_workflow_command import WorkflowCommandBase


class CreateWorkflowCommand(WorkflowCommandBase):
    def execute(self, workflow_data: WorkflowCreate) -> Workflow:
        """Create a new workflow with its initial version and optional nodes."""
        # Create the workflow using the service
        workflow = self.workflow_service.create_workflow(workflow_data)

        # Create the initial workflow version with the same active status as the workflow
        workflow_version_service = WorkflowVersionService(self.db)
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
        workflow = self.workflow_service.set_active_version(
            workflow.id, workflow_version.id
        )

        return workflow
