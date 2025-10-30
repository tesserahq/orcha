"""Command for creating a workflow with an initial workflow version."""

from sqlalchemy.orm import Session
from app.schemas.workflow import (
    Workflow,
    WorkflowCreate,
    WorkflowUpdate,
)
from app.schemas.workflow_version import WorkflowVersionCreate
from app.services.workflow_service import WorkflowService
from app.services.workflow_version_service import WorkflowVersionService


class CreateWorkflowCommand:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, workflow_data: WorkflowCreate) -> Workflow:
        # Create the workflow using the service
        workflow_service = WorkflowService(self.db)
        workflow = workflow_service.create_workflow(workflow_data)

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

        workflow = workflow_service.update_workflow(
            workflow.id, WorkflowUpdate(active_version_id=workflow_version.id)
        )

        return workflow
