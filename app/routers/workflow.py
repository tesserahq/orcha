from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
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
    WorkflowExecuteRequest,
    WorkflowExecuteResponse,
)
from app.services.workflow_service import WorkflowService
from app.commands.workflow import (
    CreateWorkflowCommand,
    UpdateWorkflowCommand,
    ExecuteWorkflowCommand,
)
from app.services.node_service import NodeService
from app.schemas.node import Node as NodeSchema
from app.auth.rbac import build_rbac_dependencies


async def infer_domain(request: Request) -> Optional[str]:
    return "*"


RESOURCE = "workflow"
rbac = build_rbac_dependencies(
    resource=RESOURCE,
    domain_resolver=infer_domain,
)

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=WorkflowWithNodes, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow_data: WorkflowCreate,
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["create"]),
):
    """Create a new workflow with its initial version."""
    command = CreateWorkflowCommand(db)
    created_workflow = command.execute(workflow_data)

    nodes: list = []
    if created_workflow.active_version_id:
        node_service = NodeService(db)
        # get_nodes_by_workflow_version returns descending by created_at; reverse for ascending order
        nodes_desc = node_service.get_nodes_by_workflow_version(
            created_workflow.active_version_id
        )
        nodes = list(reversed(nodes_desc))

    wf_schema = Workflow.model_validate(created_workflow, from_attributes=True)
    node_schemas = [NodeSchema.model_validate(n, from_attributes=True) for n in nodes]
    return WorkflowWithNodes(**wf_schema.model_dump(), nodes=node_schemas)


@router.get("", response_model=Page[Workflow])
def list_workflows(
    db: Session = Depends(get_db), _authorized: bool = Depends(rbac["read"])
):
    """List all workflows."""
    return paginate(db, WorkflowService(db).get_workflows_query())


@router.get("/{workflow_id}", response_model=WorkflowWithNodes)
def get_workflow(
    workflow: Workflow = Depends(get_workflow_by_id),
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["read"]),
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


@router.put("/{workflow_id}", response_model=WorkflowWithNodes)
def update_workflow(
    workflow_data: WorkflowUpdateRequest,
    db: Session = Depends(get_db),
    workflow: Workflow = Depends(get_workflow_by_id),
    _authorized: bool = Depends(rbac["update"]),
):
    """Update a workflow."""
    command = UpdateWorkflowCommand(db)
    updated_workflow = command.execute(workflow.id, workflow_data)

    nodes: list = []
    if updated_workflow.active_version_id:
        node_service = NodeService(db)
        # get_nodes_by_workflow_version returns descending by created_at; reverse for ascending order
        nodes_desc = node_service.get_nodes_by_workflow_version(
            updated_workflow.active_version_id
        )
        nodes = list(reversed(nodes_desc))

    wf_schema = Workflow.model_validate(updated_workflow, from_attributes=True)
    node_schemas = [NodeSchema.model_validate(n, from_attributes=True) for n in nodes]
    return WorkflowWithNodes(**wf_schema.model_dump(), nodes=node_schemas)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    workflow: Workflow = Depends(get_workflow_by_id),
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["delete"]),
):
    """Delete a workflow (soft delete)."""
    WorkflowService(db).delete_workflow(workflow.id)
    return None


@router.post("/{workflow_id}/execute", response_model=WorkflowExecuteResponse)
def execute_workflow(
    workflow_id: UUID,
    execute_data: WorkflowExecuteRequest,
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["read"]),
):
    """Execute a workflow."""
    try:
        command = ExecuteWorkflowCommand(db)
        result = command.execute(
            workflow_id=workflow_id,
            initial_data=execute_data.initial_data,
            manual=execute_data.manual,
        )
        return WorkflowExecuteResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
