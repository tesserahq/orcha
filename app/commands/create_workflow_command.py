"""Command for creating a workflow with an initial workflow version."""

from sqlalchemy.orm import Session
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate
from app.schemas.workflow_version import WorkflowVersionCreate
from app.services.workflow_service import WorkflowService
from app.services.workflow_version_service import WorkflowVersionService


def create_workflow_with_version(
    workflow_data: WorkflowCreate,
    db: Session = None,
) -> Workflow:
    """
    Create a workflow with its initial workflow version.

    This command creates both a workflow and its first version (version 1)
    in a single database transaction. This ensures that every workflow
    is created with at least one version.

    The initial version's active status will match the workflow's active status.

    Args:
        workflow_data: The workflow data to create
        db: Database session

    Returns:
        Workflow: The created workflow

    Raises:
        ValueError: If database session is not provided
    """
    if db is None:
        raise ValueError("Database session is required")

    # Create the workflow using the service
    workflow_service = WorkflowService(db)
    workflow = workflow_service.create_workflow(workflow_data)

    # Create the initial workflow version with the same active status as the workflow
    workflow_version_service = WorkflowVersionService(db)
    version_data = WorkflowVersionCreate(
        workflow_id=workflow.id,
        version=1,
        is_active=workflow_data.is_active,
    )
    workflow_version_service.create_workflow_version(version_data)

    return workflow
