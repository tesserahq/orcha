from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate
from app.services.soft_delete_service import SoftDeleteService
from app.utils.db.filtering import apply_filters


class SourceService(SoftDeleteService[Source]):
    """Service class for managing source CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize the source service.

        Args:
            db: Database session
        """
        super().__init__(db, Source)

    def get_source(self, source_id: UUID) -> Optional[Source]:
        """
        Get a single source by ID.

        Args:
            source_id: The ID of the source to retrieve

        Returns:
            Optional[Source]: The source or None if not found
        """
        return self.db.query(Source).filter(Source.id == source_id).first()

    def get_source_by_identifier(self, identifier: str) -> Optional[Source]:
        """
        Get a source by identifier.

        Args:
            identifier: The identifier of the source to retrieve

        Returns:
            Optional[Source]: The source or None if not found
        """
        return self.db.query(Source).filter(Source.identifier == identifier).first()

    def get_sources(self, skip: int = 0, limit: int = 100) -> List[Source]:
        """
        Get a list of sources with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Source]: List of sources
        """
        return (
            self.db.query(Source)
            .order_by(Source.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_sources_query(self):
        """
        Get a query for all sources.
        This is useful for pagination with fastapi-pagination.

        Returns:
            Select: SQLAlchemy select statement for sources
        """
        return select(Source).order_by(Source.created_at.desc())

    def create_source(self, source: SourceCreate) -> Source:
        """
        Create a new source.

        Args:
            source: The source data to create

        Returns:
            Source: The created source
        """
        db_source = Source(**source.model_dump())
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)
        return db_source

    def update_source(self, source_id: UUID, source: SourceUpdate) -> Optional[Source]:
        """
        Update an existing source.

        Args:
            source_id: The ID of the source to update
            source: The updated source data

        Returns:
            Optional[Source]: The updated source or None if not found
        """
        db_source = self.db.query(Source).filter(Source.id == source_id).first()
        if db_source:
            update_data = source.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_source, key, value)
            self.db.commit()
            self.db.refresh(db_source)
        return db_source

    def delete_source(self, source_id: UUID) -> bool:
        """
        Soft delete a source.

        Args:
            source_id: The ID of the source to delete

        Returns:
            bool: True if the source was deleted, False otherwise
        """
        return self.delete_record(source_id)

    def search(self, filters: dict) -> List[Source]:
        """
        Search sources based on dynamic filter criteria.

        Args:
            filters: A dictionary where keys are field names and values are either:
                - A direct value (e.g. {"name": "test"})
                - A dictionary with 'operator' and 'value' keys (e.g. {"name": {"operator": "ilike", "value": "%test%"}})

        Returns:
            List[Source]: Filtered list of sources matching the criteria.
        """
        query = self.db.query(Source)
        query = apply_filters(query, Source, filters)
        return query.all()

    def restore_source(self, source_id: UUID) -> bool:
        """Restore a soft-deleted source by setting deleted_at to None."""
        return self.restore_record(source_id)

    def hard_delete_source(self, source_id: UUID) -> bool:
        """Permanently delete a source from the database."""
        return self.hard_delete_record(source_id)

    def get_deleted_sources(self, skip: int = 0, limit: int = 100) -> List[Source]:
        """Get all soft-deleted sources."""
        return self.get_deleted_records(skip, limit)

    def get_deleted_source(self, source_id: UUID) -> Optional[Source]:
        """Get a single soft-deleted source by ID."""
        return self.get_deleted_record(source_id)

    def get_sources_deleted_after(self, date) -> List[Source]:
        """Get sources deleted after a specific date."""
        return self.get_records_deleted_after(date)
