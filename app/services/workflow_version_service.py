from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.workflow_version import WorkflowVersion
from app.schemas.workflow_version import (
    WorkflowVersionCreate,
    WorkflowVersionUpdate,
)
from app.services.soft_delete_service import SoftDeleteService
from app.utils.db.filtering import apply_filters


class WorkflowVersionService(SoftDeleteService[WorkflowVersion]):
    """Service class for managing workflow version CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize the workflow version service.

        Args:
            db: Database session
        """
        super().__init__(db, WorkflowVersion)

    def get_workflow_version(
        self, workflow_version_id: UUID
    ) -> Optional[WorkflowVersion]:
        """
        Get a single workflow version by ID.

        Args:
            workflow_version_id: The ID of the workflow version to retrieve

        Returns:
            Optional[WorkflowVersion]: The workflow version or None if not found
        """
        return (
            self.db.query(WorkflowVersion)
            .filter(WorkflowVersion.id == workflow_version_id)
            .first()
        )

    def get_workflow_versions(
        self, skip: int = 0, limit: int = 100
    ) -> List[WorkflowVersion]:
        """
        Get a list of workflow versions with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[WorkflowVersion]: List of workflow versions
        """
        return (
            self.db.query(WorkflowVersion)
            .order_by(WorkflowVersion.version.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_workflow_versions_query(self):
        """
        Get a query for all workflow versions.
        This is useful for pagination with fastapi-pagination.

        Returns:
            Select: SQLAlchemy select statement for workflow versions
        """
        return select(WorkflowVersion).order_by(WorkflowVersion.version.desc())

    def get_workflow_versions_by_workflow(
        self, workflow_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[WorkflowVersion]:
        """
        Get all workflow versions for a specific workflow.

        Args:
            workflow_id: The ID of the workflow
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[WorkflowVersion]: List of workflow versions for the workflow
        """
        return (
            self.db.query(WorkflowVersion)
            .filter(WorkflowVersion.workflow_id == workflow_id)
            .order_by(WorkflowVersion.version.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_workflow_versions(
        self, skip: int = 0, limit: int = 100
    ) -> List[WorkflowVersion]:
        """
        Get all active workflow versions.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[WorkflowVersion]: List of active workflow versions
        """
        return (
            self.db.query(WorkflowVersion)
            .filter(WorkflowVersion.is_active == True)
            .order_by(WorkflowVersion.version.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_workflow_version(
        self, workflow_version: WorkflowVersionCreate
    ) -> WorkflowVersion:
        """
        Create a new workflow version.

        Args:
            workflow_version: The workflow version data to create

        Returns:
            WorkflowVersion: The created workflow version
        """
        # Auto-increment version if not provided
        # We could run into a race condition here if two requests are made at the same time
        # but we can live with that for now
        if workflow_version.version is None:
            workflow_version.version = self.get_next_version(
                workflow_version.workflow_id
            )

        db_workflow_version = WorkflowVersion(**workflow_version.model_dump())
        self.db.add(db_workflow_version)
        self.db.commit()
        self.db.refresh(db_workflow_version)
        return db_workflow_version

    def update_workflow_version(
        self, workflow_version_id: UUID, workflow_version: WorkflowVersionUpdate
    ) -> Optional[WorkflowVersion]:
        """
        Update an existing workflow version.

        Args:
            workflow_version_id: The ID of the workflow version to update
            workflow_version: The updated workflow version data

        Returns:
            Optional[WorkflowVersion]: The updated workflow version or None if not found
        """
        db_workflow_version = (
            self.db.query(WorkflowVersion)
            .filter(WorkflowVersion.id == workflow_version_id)
            .first()
        )
        if db_workflow_version:
            update_data = workflow_version.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_workflow_version, key, value)
            self.db.commit()
            self.db.refresh(db_workflow_version)
        return db_workflow_version

    def delete_workflow_version(self, workflow_version_id: UUID) -> bool:
        """
        Soft delete a workflow version.

        Args:
            workflow_version_id: The ID of the workflow version to delete

        Returns:
            bool: True if the workflow version was deleted, False otherwise
        """
        return self.delete_record(workflow_version_id)

    def search(self, filters: dict) -> List[WorkflowVersion]:
        """
        Search workflow versions based on dynamic filter criteria.

        Args:
            filters: A dictionary where keys are field names and values are either:
                - A direct value (e.g. {"version": 1})
                - A dictionary with 'operator' and 'value' keys (e.g. {"version": {"operator": ">=", "value": 1}})

        Returns:
            List[WorkflowVersion]: Filtered list of workflow versions matching the criteria.
        """
        query = self.db.query(WorkflowVersion)
        query = apply_filters(query, WorkflowVersion, filters)
        return query.all()

    def restore_workflow_version(self, workflow_version_id: UUID) -> bool:
        """Restore a soft-deleted workflow version by setting deleted_at to None."""
        return self.restore_record(workflow_version_id)

    def hard_delete_workflow_version(self, workflow_version_id: UUID) -> bool:
        """Permanently delete a workflow version from the database."""
        return self.hard_delete_record(workflow_version_id)

    def get_deleted_workflow_versions(
        self, skip: int = 0, limit: int = 100
    ) -> List[WorkflowVersion]:
        """Get all soft-deleted workflow versions."""
        return self.get_deleted_records(skip, limit)

    def get_deleted_workflow_version(
        self, workflow_version_id: UUID
    ) -> Optional[WorkflowVersion]:
        """Get a single soft-deleted workflow version by ID."""
        return self.get_deleted_record(workflow_version_id)

    def get_workflow_versions_deleted_after(self, date) -> List[WorkflowVersion]:
        """Get workflow versions deleted after a specific date."""
        return self.get_records_deleted_after(date)

    def toggle_workflow_version_active_status(
        self, workflow_version_id: UUID
    ) -> Optional[WorkflowVersion]:
        """
        Toggle the active status of a workflow version.

        Args:
            workflow_version_id: The ID of the workflow version to toggle

        Returns:
            Optional[WorkflowVersion]: The updated workflow version or None if not found
        """
        db_workflow_version = (
            self.db.query(WorkflowVersion)
            .filter(WorkflowVersion.id == workflow_version_id)
            .first()
        )
        if db_workflow_version:
            db_workflow_version.is_active = not db_workflow_version.is_active
            self.db.commit()
            self.db.refresh(db_workflow_version)
        return db_workflow_version

    def get_next_version(self, workflow_id: UUID) -> int:
        """Get the next version number for a workflow."""
        latest_version = (
            self.db.query(WorkflowVersion)
            .filter(WorkflowVersion.workflow_id == workflow_id)
            .order_by(WorkflowVersion.version.desc())
            .first()
        )
        if latest_version:
            return latest_version.version + 1
        else:
            return 1
