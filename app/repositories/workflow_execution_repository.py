from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.workflow_execution import WorkflowExecution


class WorkflowExecutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_execution(self, execution_id: UUID) -> Optional[WorkflowExecution]:
        return (
            self.db.query(WorkflowExecution)
            .filter(WorkflowExecution.id == execution_id)
            .first()
        )

    def get_executions_by_workflow(self, workflow_id: UUID) -> "select":
        return (
            select(WorkflowExecution)
            .where(WorkflowExecution.workflow_id == workflow_id)
            .order_by(WorkflowExecution.started_at.desc())
        )

    def create_execution(self, execution: WorkflowExecution) -> WorkflowExecution:
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
