from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.routers.utils.dependencies import get_workflow_by_id
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page


from app.db import get_db
from app.schemas.workflow import (
    Workflow,
    WorkflowCreate,
    WorkflowUpdateRequest,
    WorkflowWithNodes,
)
from app.services.workflow_service import WorkflowService
from app.commands.create_workflow_command import CreateWorkflowCommand
from app.commands.update_workflow_command import UpdateWorkflowCommand
from app.services.node_service import NodeService
from app.services.workflow_version_service import WorkflowVersionService
from app.schemas.node import Node as NodeSchema

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


@router.get("/{workflow_id}", response_model=WorkflowWithNodes)
def get_workflow(
    workflow: Workflow = Depends(get_workflow_by_id), db: Session = Depends(get_db)
):
    """Get a workflow by ID, including ordered nodes for its active version."""
    nodes: list = []
    if workflow.active_version_id:
        node_service = NodeService(db)
        # get_nodes_by_workflow_version returns descending by created_at; reverse for ascending order
        nodes_desc = node_service.get_nodes_by_workflow_version(
            workflow.active_version_id
        )
        nodes = list(reversed(nodes_desc))

    wf_schema = Workflow.model_validate(workflow, from_attributes=True)
    node_schemas = [NodeSchema.model_validate(n, from_attributes=True) for n in nodes]
    return WorkflowWithNodes(**wf_schema.model_dump(), nodes=node_schemas)


@router.put("/{workflow_id}", response_model=Workflow)
def update_workflow(
    workflow_data: WorkflowUpdateRequest,
    db: Session = Depends(get_db),
    workflow: Workflow = Depends(get_workflow_by_id),
):
    """Update a workflow."""
    command = UpdateWorkflowCommand(db)
    return command.execute(workflow.id, workflow_data)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    workflow: Workflow = Depends(get_workflow_by_id), db: Session = Depends(get_db)
):
    """Delete a workflow (soft delete)."""
    WorkflowService(db).delete_workflow(workflow.id)
    return None
