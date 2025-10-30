from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page


from app.db import get_db
from app.schemas.workflow import (
    Workflow,
    WorkflowCreate,
    WorkflowUpdateRequest,
)
from app.services.workflow_service import WorkflowService
from app.commands.create_workflow_command import CreateWorkflowCommand

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=Workflow, status_code=status.HTTP_201_CREATED)
def create_workflow(workflow_data: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow with its initial version."""
    command = CreateWorkflowCommand(db)
    created_workflow = command.execute(workflow_data)
    return created_workflow


@router.get("", response_model=Page[Workflow])
def list_workflows(db: Session = Depends(get_db)):
    """List all workflows."""
    return paginate(db, WorkflowService(db).get_workflows_query())


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
    workflow_id: UUID, workflow: WorkflowUpdateRequest, db: Session = Depends(get_db)
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
