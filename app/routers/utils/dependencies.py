from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.models.workflow import Workflow
from app.services.workflow_service import WorkflowService


def get_workflow_by_id(
    workflow_id: UUID,
    db: Session = Depends(get_db),
) -> Workflow:
    """FastAPI dependency to get a workflow by ID.

    Args:
        workflow_id: The UUID of the workflow to retrieve
        db: Database session dependency

    Returns:
        Workflow: The retrieved workflow

    Raises:
        HTTPException: If the workflow is not found
    """
    workflow = WorkflowService(db).get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
