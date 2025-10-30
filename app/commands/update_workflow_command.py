"""Command for updating an existing workflow."""

from uuid import UUID
from sqlalchemy.orm import Session
from app.schemas.workflow import Workflow, WorkflowUpdate, WorkflowUpdateRequest
from app.schemas.workflow_version import WorkflowVersionCreate
from app.services.workflow_service import WorkflowService
from app.services.workflow_version_service import WorkflowVersionService


class UpdateWorkflowCommand:
    def __init__(self, db: Session):
        self.db = db
        self.workflow_service = WorkflowService(self.db)

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

        # Set the new version as the active version
        updated_workflow = self.workflow_service.update_workflow(
            workflow.id, WorkflowUpdate(active_version_id=workflow_version.id)
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
