from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.schemas.workflow import Workflow, WorkflowCreate, WorkflowUpdate
from app.services.workflow_service import WorkflowService
from app.schemas.common import ListResponse

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=Workflow, status_code=status.HTTP_201_CREATED)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow."""
    workflow_service = WorkflowService(db)
    return workflow_service.create_workflow(workflow)


@router.get("", response_model=ListResponse[Workflow])
def list_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all workflows."""
    workflows = WorkflowService(db).get_workflows(skip=skip, limit=limit)
    return ListResponse(data=workflows)


@router.get("/{workflow_id}", response_model=Workflow)
def get_workflow(workflow_id: UUID, db: Session = Depends(get_db)):
    """Get a workflow by ID."""
    workflow = WorkflowService(db).get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found"
        )
    return workflow


@router.put("/{workflow_id}", response_model=Workflow)
def update_workflow(
    workflow_id: UUID, workflow: WorkflowUpdate, db: Session = Depends(get_db)
):
    """Update a workflow."""
    workflow_service = WorkflowService(db)
    updated_workflow = workflow_service.update_workflow(workflow_id, workflow)
    if not updated_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found"
        )
    return updated_workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_id: UUID, db: Session = Depends(get_db)):
    """Delete a workflow (soft delete)."""
    if not WorkflowService(db).delete_workflow(workflow_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found"
        )
