from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate
from app.services.soft_delete_service import SoftDeleteService
from app.utils.db.filtering import apply_filters


class WorkflowService(SoftDeleteService[Workflow]):
    """Service class for managing workflow CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize the workflow service.

        Args:
            db: Database session
        """
        super().__init__(db, Workflow)

    def get_workflow(self, workflow_id: UUID) -> Optional[Workflow]:
        """
        Get a single workflow by ID.

        Args:
            workflow_id: The ID of the workflow to retrieve

        Returns:
            Optional[Workflow]: The workflow or None if not found
        """
        return self.db.query(Workflow).filter(Workflow.id == workflow_id).first()

    def get_workflows(self, skip: int = 0, limit: int = 100) -> List[Workflow]:
        """
        Get a list of workflows with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Workflow]: List of workflows
        """
        return (
            self.db.query(Workflow)
            .order_by(Workflow.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_workflows_query(self):
        """
        Get a query for all workflows.
        This is useful for pagination with fastapi-pagination.

        Returns:
            Select: SQLAlchemy select statement for workflows
        """
        return select(Workflow).order_by(Workflow.created_at.desc())

    def get_active_workflows(self, skip: int = 0, limit: int = 100) -> List[Workflow]:
        """
        Get all active workflows.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Workflow]: List of active workflows
        """
        return (
            self.db.query(Workflow)
            .filter(Workflow.is_active == True)
            .order_by(Workflow.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_workflows_by_trigger_event_type(
        self, event_type: str, skip: int = 0, limit: int = 100
    ) -> List[Workflow]:
        """
        Get all workflows that trigger on a specific event type.

        Args:
            event_type: The event type to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Workflow]: List of workflows for the event type
        """
        return (
            self.db.query(Workflow)
            .filter(Workflow.trigger_event_type == event_type)
            .order_by(Workflow.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_workflow(self, workflow: WorkflowCreate) -> Workflow:
        """
        Create a new workflow.

        Args:
            workflow: The workflow data to create

        Returns:
            Workflow: The created workflow
        """
        db_workflow = Workflow(**workflow.model_dump())
        self.db.add(db_workflow)
        self.db.commit()
        self.db.refresh(db_workflow)
        return db_workflow

    def update_workflow(
        self, workflow_id: UUID, workflow: WorkflowUpdate
    ) -> Optional[Workflow]:
        """
        Update an existing workflow.

        Args:
            workflow_id: The ID of the workflow to update
            workflow: The updated workflow data

        Returns:
            Optional[Workflow]: The updated workflow or None if not found
        """
        db_workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if db_workflow:
            update_data = workflow.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_workflow, key, value)
            self.db.commit()
            self.db.refresh(db_workflow)

        return db_workflow

    def delete_workflow(self, workflow_id: UUID) -> bool:
        """
        Soft delete a workflow.

        Args:
            workflow_id: The ID of the workflow to delete

        Returns:
            bool: True if the workflow was deleted, False otherwise
        """
        return self.delete_record(workflow_id)

    def search(self, filters: dict) -> List[Workflow]:
        """
        Search workflows based on dynamic filter criteria.

        Args:
            filters: A dictionary where keys are field names and values are either:
                - A direct value (e.g. {"name": "My Workflow"})
                - A dictionary with 'operator' and 'value' keys (e.g. {"name": {"operator": "ilike", "value": "%workflow%"}})

        Returns:
            List[Workflow]: Filtered list of workflows matching the criteria.
        """
        query = self.db.query(Workflow)
        query = apply_filters(query, Workflow, filters)
        return query.all()

    def restore_workflow(self, workflow_id: UUID) -> bool:
        """Restore a soft-deleted workflow by setting deleted_at to None."""
        return self.restore_record(workflow_id)

    def hard_delete_workflow(self, workflow_id: UUID) -> bool:
        """Permanently delete a workflow from the database."""
        return self.hard_delete_record(workflow_id)

    def get_deleted_workflows(self, skip: int = 0, limit: int = 100) -> List[Workflow]:
        """Get all soft-deleted workflows."""
        return self.get_deleted_records(skip, limit)

    def get_deleted_workflow(self, workflow_id: UUID) -> Optional[Workflow]:
        """Get a single soft-deleted workflow by ID."""
        return self.get_deleted_record(workflow_id)

    def get_workflows_deleted_after(self, date) -> List[Workflow]:
        """Get workflows deleted after a specific date."""
        return self.get_records_deleted_after(date)

    def toggle_workflow_active_status(self, workflow_id: UUID) -> Optional[Workflow]:
        """
        Toggle the active status of a workflow.

        Args:
            workflow_id: The ID of the workflow to toggle

        Returns:
            Optional[Workflow]: The updated workflow or None if not found
        """
        db_workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if db_workflow:
            db_workflow.is_active = not db_workflow.is_active
            self.db.commit()
            self.db.refresh(db_workflow)
        return db_workflow
