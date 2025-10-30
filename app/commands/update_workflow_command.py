"""Command for updating an existing workflow."""

from uuid import UUID
from sqlalchemy.orm import Session
from app.schemas.workflow import Workflow, WorkflowUpdateRequest
from app.services.workflow_service import WorkflowService


class UpdateWorkflowCommand:
    def __init__(self, db: Session):
        self.db = db

    def execute(
        self, workflow_id: UUID, workflow_data: WorkflowUpdateRequest
    ) -> Workflow:
        """Update an existing workflow and return the updated entity."""
        workflow_service = WorkflowService(self.db)
        updated_workflow = workflow_service.update_workflow(workflow_id, workflow_data)
        return updated_workflow
