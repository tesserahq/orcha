"""Command for running a workflow execution."""

from uuid import UUID
from typing import Dict, Any, List, Set
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.models.node import Node
from app.models.edge import Edge
from app.services.workflow_service import WorkflowService
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService
from app.schemas.workflow import WorkflowUpdate
from app.constants.workflow_execution_status import WorkflowExecutionStatus
from app.constants.node_kinds import NODE_BY_ID, ExecutionData
from app.exceptions.resource_not_found_error import ResourceNotFoundError


class RunWorkflowCommand:
    """Command for executing a workflow with JSON data."""

    def __init__(self, db: Session):
        """
        Initialize the run workflow command.

        Args:
            db: Database session
        """
        self.db = db
        self.workflow_service = WorkflowService(self.db)
        self.node_service = NodeService(self.db)
        self.edge_service = EdgeService(self.db)

    def execute(self, workflow_id: UUID, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with the provided JSON data.

        Args:
            workflow_id: The ID of the workflow to execute
            input_data: JSON data to pass through the workflow

        Returns:
            Dict containing execution result and status

        Raises:
            ResourceNotFoundError: If workflow or active version not found
        """
        # Get workflow
        workflow = self.workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise ResourceNotFoundError(f"Workflow with id {workflow_id} not found")

        # Check if workflow has an active version
        if not workflow.active_version_id:
            raise ResourceNotFoundError(
                f"Workflow {workflow_id} does not have an active version"
            )

        # Update workflow status to running
        workflow = self.workflow_service.update_workflow(
            workflow_id,
            WorkflowUpdate(
                execution_status=WorkflowExecutionStatus.RUNNING,
                execution_status_message=None,
                last_execution_time=datetime.utcnow(),
            ),
        )

        try:
            # Get all nodes and edges for the active version
            nodes = self.node_service.get_nodes_by_workflow_version(
                workflow.active_version_id
            )
            edges = self.edge_service.get_edges_by_workflow_version(
                workflow.active_version_id
            )

            if not nodes:
                raise ValueError("Workflow has no nodes to execute")

            # Build graph structure
            node_map = {node.id: node for node in nodes}
            incoming_edges_map: Dict[UUID, List[Edge]] = {}
            outgoing_edges_map: Dict[UUID, List[Edge]] = {}

            for edge in edges:
                # Map incoming edges (target_node_id -> list of edges)
                if edge.target_node_id not in incoming_edges_map:
                    incoming_edges_map[edge.target_node_id] = []
                incoming_edges_map[edge.target_node_id].append(edge)

                # Map outgoing edges (source_node_id -> list of edges)
                if edge.source_node_id not in outgoing_edges_map:
                    outgoing_edges_map[edge.source_node_id] = []
                outgoing_edges_map[edge.source_node_id].append(edge)

            # Find trigger nodes (nodes with no incoming edges)
            trigger_nodes = [
                node
                for node in nodes
                if node.id not in incoming_edges_map
                or len(incoming_edges_map[node.id]) == 0
            ]

            if not trigger_nodes:
                raise ValueError("Workflow has no trigger nodes (nodes with no incoming edges)")

            # Execute workflow starting from trigger nodes
            execution_data = ExecutionData(json=input_data)
            result_data = self._execute_nodes(
                trigger_nodes, node_map, incoming_edges_map, outgoing_edges_map, execution_data
            )

            # Update workflow status to success
            workflow = self.workflow_service.update_workflow(
                workflow_id,
                WorkflowUpdate(
                    execution_status=WorkflowExecutionStatus.SUCCESS,
                    execution_status_message=None,
                ),
            )

            return {
                "status": WorkflowExecutionStatus.SUCCESS,
                "data": result_data.json if result_data else input_data,
                "error": None,
            }

        except Exception as e:
            # Update workflow status to failed
            error_message = str(e)
            workflow = self.workflow_service.update_workflow(
                workflow_id,
                WorkflowUpdate(
                    execution_status=WorkflowExecutionStatus.FAILED,
                    execution_status_message=error_message,
                ),
            )

            return {
                "status": WorkflowExecutionStatus.FAILED,
                "data": None,
                "error": error_message,
            }

    def _execute_nodes(
        self,
        start_nodes: List[Node],
        node_map: Dict[UUID, Node],
        incoming_edges_map: Dict[UUID, List[Edge]],
        outgoing_edges_map: Dict[UUID, List[Edge]],
        execution_data: ExecutionData,
    ) -> ExecutionData:
        """
        Execute nodes starting from the given start nodes.

        Args:
            start_nodes: List of nodes to start execution from
            node_map: Dictionary mapping node IDs to Node objects
            incoming_edges_map: Dictionary mapping node IDs to their incoming edges
            outgoing_edges_map: Dictionary mapping node IDs to their outgoing edges
            execution_data: The execution data to pass through nodes

        Returns:
            ExecutionData: The final execution data after all nodes have been executed

        Raises:
            Exception: If any node returns an error
        """
        executed: Set[UUID] = set()
        queue: List[Node] = start_nodes.copy()
        current_data = execution_data
        max_iterations = len(node_map) * 2  # Safety check to prevent infinite loops
        iteration_count = 0

        while queue and iteration_count < max_iterations:
            iteration_count += 1
            node = queue.pop(0)

            # Skip if already executed
            if node.id in executed:
                continue

            # Check if all incoming nodes have been executed
            incoming_node_ids = set()
            if node.id in incoming_edges_map:
                for edge in incoming_edges_map[node.id]:
                    incoming_node_ids.add(edge.source_node_id)

            # If this node has dependencies, check if they're all executed
            if incoming_node_ids and not incoming_node_ids.issubset(executed):
                # Not all dependencies are executed, skip for now
                # Add back to queue to retry later
                queue.append(node)
                continue

            # Get node kind definition
            node_kind = NODE_BY_ID.get(node.kind)
            if not node_kind:
                raise ValueError(f"Node kind '{node.kind}' not found")

            # Execute the node
            try:
                result = node_kind.description.execute(current_data)
            except Exception as e:
                # Wrap node execution errors
                raise Exception(
                    f"Error executing node '{node.name}' (id: {node.id}): {str(e)}"
                ) from e

            # Check if node returned an error
            if result.error:
                raise Exception(
                    f"Node '{node.name}' (id: {node.id}) returned error: {result.error}"
                )

            # Mark node as executed
            executed.add(node.id)

            # Update current data with result
            current_data = result

            # Get next nodes to execute (nodes connected via outgoing edges)
            if node.id in outgoing_edges_map:
                for edge in outgoing_edges_map[node.id]:
                    target_node = node_map.get(edge.target_node_id)
                    if target_node and target_node.id not in executed:
                        # Add to queue if not already there
                        if target_node not in queue:
                            queue.append(target_node)

        # Check if we hit the max iterations (possible cycle or missing dependencies)
        if iteration_count >= max_iterations and queue:
            raise Exception(
                f"Workflow execution reached maximum iterations. "
                f"Possible cycle or missing dependencies. "
                f"Remaining nodes: {[n.name for n in queue]}"
            )

        return current_data

