from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.schemas.node import NodeCreatePayload
from app.schemas.node import Node


class WorkflowBase(BaseModel):
    """Base workflow model containing common workflow attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the workflow. Defaults to None."""

    name: str
    """Name of the workflow. Required field."""

    description: Optional[str] = None
    """Description of the workflow. Optional field."""

    is_active: bool = True
    """Whether the workflow is active. Defaults to True."""

    active_version_id: Optional[UUID] = None
    """ID of the active version of the workflow. Optional field."""

    last_execution_time: Optional[datetime] = None
    """Timestamp of the last execution of the workflow. Optional field."""

    execution_status: Optional[str] = None
    """Status of the last execution of the workflow. Optional field."""

    execution_status_message: Optional[str] = None
    """Message of the last execution of the workflow. Optional field."""


class WorkflowCreate(WorkflowBase):
    """Schema for creating a new workflow. Inherits all fields from WorkflowBase."""

    nodes: Optional[List[NodeCreatePayload]] = None
    """Ordered nodes to associate with the initial workflow version. Optional."""


class WorkflowUpdate(BaseModel):
    """Schema for updating an existing workflow. All fields are optional."""

    name: Optional[str] = None
    """Updated workflow name."""

    description: Optional[str] = None
    """Updated workflow description."""

    is_active: Optional[bool] = None
    """Updated active status."""

    active_version_id: Optional[UUID] = None
    """Updated active version ID."""

    last_execution_time: Optional[datetime] = None
    """Updated timestamp of the last execution of the workflow. Optional field."""

    execution_status: Optional[str] = None
    """Updated status of the last execution of the workflow. Optional field."""

    execution_status_message: Optional[str] = None
    """Updated message of the last execution of the workflow. Optional field."""


class WorkflowUpdateRequest(BaseModel):
    """Schema for updating an existing workflow. All fields are optional."""

    name: Optional[str] = None
    """Updated workflow name."""

    description: Optional[str] = None
    """Updated workflow description."""

    is_active: Optional[bool] = None
    """Updated active status."""

    nodes: Optional[List[NodeCreatePayload]] = None
    """Ordered nodes to associate with the new workflow version. Optional."""


class WorkflowInDB(WorkflowBase):
    """Schema representing a workflow as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the workflow in the database."""

    created_at: datetime
    """Timestamp when the workflow record was created."""

    updated_at: datetime
    """Timestamp when the workflow record was last updated."""

    model_config = {"from_attributes": True}


class Workflow(WorkflowInDB):
    """Schema for workflow data returned in API responses. Inherits all fields from WorkflowInDB."""

    pass


class WorkflowWithNodes(Workflow):
    """Workflow response including ordered nodes for the active version."""

    nodes: List[Node]


class WorkflowExecuteRequest(BaseModel):
    """Schema for executing a workflow."""

    initial_data: Optional[Dict[str, Any]] = None
    """Optional initial data to pass to trigger nodes."""

    manual: bool = False
    """Whether this is a manual execution (bypasses is_active check)."""


class NodeExecutionResult(BaseModel):
    """Schema for a single node execution result."""

    node_id: str
    """ID of the executed node."""

    node_name: str
    """Name of the executed node."""

    node_kind: str
    """Kind of the executed node."""

    status: str
    """Execution status (success or error)."""

    data: Optional[Dict[str, Any]] = None
    """Output data from the node execution."""

    error: Optional[str] = None
    """Error message if execution failed."""


class TriggerExecutionResult(BaseModel):
    """Schema for execution results starting from a trigger node."""

    trigger_node_id: str
    """ID of the trigger node."""

    trigger_node_name: str
    """Name of the trigger node."""

    execution_results: List[NodeExecutionResult]
    """List of node execution results."""


class WorkflowExecuteResponse(BaseModel):
    """Schema for workflow execution response."""

    workflow_id: str
    """ID of the executed workflow."""

    status: str
    """Overall execution status (completed or error)."""

    results: List[TriggerExecutionResult]
    """List of execution results for each trigger node."""
