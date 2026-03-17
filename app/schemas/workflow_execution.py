from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class WorkflowExecution(BaseModel):
    id: UUID
    workflow_id: UUID
    workflow_version_id: Optional[UUID] = None
    status: str
    triggered_by: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
