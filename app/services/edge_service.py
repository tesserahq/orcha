from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.edge import Edge
from app.models.workflow import Workflow
from app.schemas.edge import EdgeCreate, EdgeUpdate
from app.services.soft_delete_service import SoftDeleteService
from app.utils.db.filtering import apply_filters
from app.exceptions.resource_not_found_error import ResourceNotFoundError


class EdgeService(SoftDeleteService[Edge]):
    """Service class for managing edge CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize the edge service.

        Args:
            db: Database session
        """
        super().__init__(db, Edge)

    def get_edge(self, edge_id: UUID) -> Optional[Edge]:
        """
        Get a single edge by ID.

        Args:
            edge_id: The ID of the edge to retrieve

        Returns:
            Optional[Edge]: The edge or None if not found
        """
        return self.db.query(Edge).filter(Edge.id == edge_id).first()

    def get_edges(self, skip: int = 0, limit: int = 100) -> List[Edge]:
        """
        Get a list of edges with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Edge]: List of edges
        """
        return (
            self.db.query(Edge)
            .order_by(Edge.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_edges_query(self):
        """
        Get a query for all edges.
        This is useful for pagination with fastapi-pagination.

        Returns:
            Select: SQLAlchemy select statement for edges
        """
        return select(Edge).order_by(Edge.created_at.desc())

    def get_edges_by_workflow_version(
        self, workflow_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Edge]:
        """
        Get all edges for a specific workflow version.

        Args:
            workflow_version_id: The ID of the workflow version
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Edge]: List of edges for the workflow version
        """
        return (
            self.db.query(Edge)
            .filter(Edge.workflow_version_id == workflow_version_id)
            .order_by(Edge.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_edges_by_workflow(
        self, workflow_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Edge]:
        """
        Get all edges for the active version of a workflow.

        Args:
            workflow_id: The ID of the workflow
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Edge]: List of edges for the workflow's active version

        Raises:
            ResourceNotFoundError: If workflow not found or has no active version
        """
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ResourceNotFoundError(f"Workflow with id {workflow_id} not found")

        if not workflow.active_version_id:
            raise ResourceNotFoundError(
                f"Workflow {workflow_id} does not have an active version"
            )

        return self.get_edges_by_workflow_version(
            workflow.active_version_id, skip=skip, limit=limit
        )

    def get_edges_by_source_node(
        self, source_node_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Edge]:
        """
        Get all edges originating from a specific source node.

        Args:
            source_node_id: The ID of the source node
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Edge]: List of edges originating from the source node
        """
        return (
            self.db.query(Edge)
            .filter(Edge.source_node_id == source_node_id)
            .order_by(Edge.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_edges_by_target_node(
        self, target_node_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Edge]:
        """
        Get all edges terminating at a specific target node.

        Args:
            target_node_id: The ID of the target node
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Edge]: List of edges terminating at the target node
        """
        return (
            self.db.query(Edge)
            .filter(Edge.target_node_id == target_node_id)
            .order_by(Edge.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_edges_by_node(
        self, node_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Edge]:
        """
        Get all edges connected to a specific node (either as source or target).

        Args:
            node_id: The ID of the node
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Edge]: List of edges connected to the node
        """
        return (
            self.db.query(Edge)
            .filter((Edge.source_node_id == node_id) | (Edge.target_node_id == node_id))
            .order_by(Edge.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_edge(self, edge: EdgeCreate) -> Edge:
        """
        Create a new edge.

        Args:
            edge: The edge data to create

        Returns:
            Edge: The created edge
        """
        db_edge = Edge(**edge.model_dump())
        self.db.add(db_edge)
        self.db.commit()
        self.db.refresh(db_edge)
        return db_edge

    def update_edge(self, edge_id: UUID, edge: EdgeUpdate) -> Optional[Edge]:
        """
        Update an existing edge.

        Args:
            edge_id: The ID of the edge to update
            edge: The updated edge data

        Returns:
            Optional[Edge]: The updated edge or None if not found
        """
        db_edge = self.db.query(Edge).filter(Edge.id == edge_id).first()
        if db_edge:
            update_data = edge.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_edge, key, value)
            self.db.commit()
            self.db.refresh(db_edge)
        return db_edge

    def delete_edge(self, edge_id: UUID) -> bool:
        """
        Soft delete an edge.

        Args:
            edge_id: The ID of the edge to delete

        Returns:
            bool: True if the edge was deleted, False otherwise
        """
        return self.delete_record(edge_id)

    def search(self, filters: dict) -> List[Edge]:
        """
        Search edges based on dynamic filter criteria.

        Args:
            filters: A dictionary where keys are field names and values are either:
                - A direct value (e.g. {"name": "My Edge"})
                - A dictionary with 'operator' and 'value' keys (e.g. {"name": {"operator": "ilike", "value": "%edge%"}})

        Returns:
            List[Edge]: Filtered list of edges matching the criteria.
        """
        query = self.db.query(Edge)
        query = apply_filters(query, Edge, filters)
        return query.all()

    def restore_edge(self, edge_id: UUID) -> bool:
        """Restore a soft-deleted edge by setting deleted_at to None."""
        return self.restore_record(edge_id)

    def hard_delete_edge(self, edge_id: UUID) -> bool:
        """Permanently delete an edge from the database."""
        return self.hard_delete_record(edge_id)

    def get_deleted_edges(self, skip: int = 0, limit: int = 100) -> List[Edge]:
        """Get all soft-deleted edges."""
        return self.get_deleted_records(skip, limit)

    def get_deleted_edge(self, edge_id: UUID) -> Optional[Edge]:
        """Get a single soft-deleted edge by ID."""
        return self.get_deleted_record(edge_id)

    def get_edges_deleted_after(self, date) -> List[Edge]:
        """Get edges deleted after a specific date."""
        return self.get_records_deleted_after(date)
