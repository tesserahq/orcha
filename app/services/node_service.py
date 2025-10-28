from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate
from app.services.soft_delete_service import SoftDeleteService
from app.utils.db.filtering import apply_filters


class NodeService(SoftDeleteService[Node]):
    """Service class for managing node CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize the node service.

        Args:
            db: Database session
        """
        super().__init__(db, Node)

    def get_node(self, node_id: UUID) -> Optional[Node]:
        """
        Get a single node by ID.

        Args:
            node_id: The ID of the node to retrieve

        Returns:
            Optional[Node]: The node or None if not found
        """
        return self.db.query(Node).filter(Node.id == node_id).first()

    def get_nodes(self, skip: int = 0, limit: int = 100) -> List[Node]:
        """
        Get a list of nodes with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Node]: List of nodes
        """
        return (
            self.db.query(Node)
            .order_by(Node.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_nodes_query(self):
        """
        Get a query for all nodes.
        This is useful for pagination with fastapi-pagination.

        Returns:
            Select: SQLAlchemy select statement for nodes
        """
        return select(Node).order_by(Node.created_at.desc())

    def get_nodes_by_workflow_version(
        self, workflow_version_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Node]:
        """
        Get all nodes for a specific workflow version.

        Args:
            workflow_version_id: The ID of the workflow version
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Node]: List of nodes for the workflow version
        """
        return (
            self.db.query(Node)
            .filter(Node.workflow_version_id == workflow_version_id)
            .order_by(Node.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_nodes_by_kind(
        self, kind: str, skip: int = 0, limit: int = 100
    ) -> List[Node]:
        """
        Get all nodes of a specific kind.

        Args:
            kind: The kind/type of node to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Node]: List of nodes of the specified kind
        """
        return (
            self.db.query(Node)
            .filter(Node.kind == kind)
            .order_by(Node.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_node(self, node: NodeCreate) -> Node:
        """
        Create a new node.

        Args:
            node: The node data to create

        Returns:
            Node: The created node
        """
        db_node = Node(**node.model_dump())
        self.db.add(db_node)
        self.db.commit()
        self.db.refresh(db_node)
        return db_node

    def update_node(self, node_id: UUID, node: NodeUpdate) -> Optional[Node]:
        """
        Update an existing node.

        Args:
            node_id: The ID of the node to update
            node: The updated node data

        Returns:
            Optional[Node]: The updated node or None if not found
        """
        db_node = self.db.query(Node).filter(Node.id == node_id).first()
        if db_node:
            update_data = node.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_node, key, value)
            self.db.commit()
            self.db.refresh(db_node)
        return db_node

    def delete_node(self, node_id: UUID) -> bool:
        """
        Soft delete a node.

        Args:
            node_id: The ID of the node to delete

        Returns:
            bool: True if the node was deleted, False otherwise
        """
        return self.delete_record(node_id)

    def search(self, filters: dict) -> List[Node]:
        """
        Search nodes based on dynamic filter criteria.

        Args:
            filters: A dictionary where keys are field names and values are either:
                - A direct value (e.g. {"name": "My Node"})
                - A dictionary with 'operator' and 'value' keys (e.g. {"name": {"operator": "ilike", "value": "%node%"}})

        Returns:
            List[Node]: Filtered list of nodes matching the criteria.
        """
        query = self.db.query(Node)
        query = apply_filters(query, Node, filters)
        return query.all()

    def restore_node(self, node_id: UUID) -> bool:
        """Restore a soft-deleted node by setting deleted_at to None."""
        return self.restore_record(node_id)

    def hard_delete_node(self, node_id: UUID) -> bool:
        """Permanently delete a node from the database."""
        return self.hard_delete_record(node_id)

    def get_deleted_nodes(self, skip: int = 0, limit: int = 100) -> List[Node]:
        """Get all soft-deleted nodes."""
        return self.get_deleted_records(skip, limit)

    def get_deleted_node(self, node_id: UUID) -> Optional[Node]:
        """Get a single soft-deleted node by ID."""
        return self.get_deleted_record(node_id)

    def get_nodes_deleted_after(self, date) -> List[Node]:
        """Get nodes deleted after a specific date."""
        return self.get_records_deleted_after(date)
