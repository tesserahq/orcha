"""Command for executing a workflow."""

from uuid import UUID
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.workflow import Workflow
from app.models.node import Node
from app.models.edge import Edge
from app.services.workflow_service import WorkflowService
from app.services.node_service import NodeService
from app.services.edge_service import EdgeService
from app.constants.node_kinds import NODE_BY_ID, CATEGORY_TRIGGER
from app.constants.node_types import ExecutionData
from app.exceptions.resource_not_found_error import ResourceNotFoundError
from app.schemas.event import EventBase


class ExecuteWorkflowCommand:
    """Command for executing a workflow."""

    def __init__(self, db: Session):
        """
        Initialize the execute workflow command.

        Args:
            db: Database session
        """
        self.db = db
        self.workflow_service = WorkflowService(self.db)
        self.node_service = NodeService(self.db)
        self.edge_service = EdgeService(self.db)

    def execute(
        self,
        workflow_id: UUID,
        initial_data: Optional[Dict[str, Any]] = None,
        manual: bool = False,
        event: Optional[EventBase] = None,
    ) -> Dict[str, Any]:
        """
        Execute a workflow.

        The workflow will only run if:
        - The workflow is active (is_active=True), OR
        - manual=True is passed

        Args:
            workflow_id: The ID of the workflow to execute
            initial_data: Optional initial data to pass to trigger nodes
            manual: Whether this is a manual execution (bypasses is_active check)
            event: Optional event to pass to trigger nodes (for event-triggered workflows)

        Returns:
            Dict containing execution results

        Raises:
            ResourceNotFoundError: If workflow is not found
            ValueError: If workflow cannot be executed
        """
        # Get the workflow
        workflow = self.workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise ResourceNotFoundError(f"Workflow with id {workflow_id} not found")

        # Check if workflow can be executed
        if not workflow.is_active and not manual:
            raise ValueError(
                f"Workflow {workflow_id} is not active and manual execution was not requested"
            )

        # Get the active workflow version
        if not workflow.active_version_id:
            raise ValueError(f"Workflow {workflow_id} has no active version")

        workflow_version_id = workflow.active_version_id

        # Get all nodes for this workflow version
        nodes = self.node_service.get_nodes_by_workflow_version(workflow_version_id)
        if not nodes:
            raise ValueError(f"Workflow version {workflow_version_id} has no nodes")

        # Get all edges for this workflow version
        edges = self.edge_service.get_edges_by_workflow_version(workflow_version_id)

        # Find trigger nodes (nodes with kind that maps to CATEGORY_TRIGGER)
        trigger_nodes = self._find_trigger_nodes(nodes)
        if not trigger_nodes:
            raise ValueError(
                f"Workflow version {workflow_version_id} has no trigger nodes"
            )

        # Prepare initial execution data
        execution_data = ExecutionData(
            json=initial_data or {},
            error=None,
            event=event,
        )

        # Execute workflow starting from trigger nodes
        execution_results = []
        has_errors = False
        for trigger_node in trigger_nodes:
            result = self._execute_node_tree(trigger_node, nodes, edges, execution_data)
            execution_results.append(result)
            # Check if any execution had errors
            for exec_result in result.get("execution_results", []):
                if exec_result.get("status") == "error":
                    has_errors = True
                    break

        # Update workflow execution status
        if has_errors:
            self._update_workflow_execution_status(
                workflow, "error", "Workflow execution completed with errors"
            )
            status = "error"
        else:
            self._update_workflow_execution_status(
                workflow, "completed", "Workflow executed successfully"
            )
            status = "completed"

        return {
            "workflow_id": str(workflow_id),
            "status": status,
            "results": execution_results,
        }

    def _find_trigger_nodes(self, nodes: List[Node]) -> List[Node]:
        """
        Find all trigger nodes in a list of nodes.

        Args:
            nodes: List of nodes to search

        Returns:
            List of trigger nodes
        """
        trigger_nodes = []
        for node in nodes:
            # Get the node definition by kind
            node_def = NODE_BY_ID.get(node.kind)

            if node_def is None:
                raise ValueError(f"Node kind {node.kind} not found")

            if node_def and node_def.category == CATEGORY_TRIGGER:
                trigger_nodes.append(node)
        return trigger_nodes

    def _execute_node_tree(
        self,
        start_node: Node,
        all_nodes: List[Node],
        all_edges: List[Edge],
        initial_data: ExecutionData,
    ) -> Dict[str, Any]:
        """
        Execute a tree of nodes starting from a trigger node.

        Args:
            start_node: The node to start execution from
            all_nodes: All nodes in the workflow version
            all_edges: All edges in the workflow version
            initial_data: Initial execution data

        Returns:
            Dict containing execution results
        """
        # Create a map of node_id -> node for quick lookup
        node_map = {node.id: node for node in all_nodes}

        # Create a map of source_node_id -> list of edges
        edge_map: Dict[UUID, List[Edge]] = {}
        for edge in all_edges:
            if edge.source_node_id not in edge_map:
                edge_map[edge.source_node_id] = []
            edge_map[edge.source_node_id].append(edge)

        # Execute nodes using BFS traversal
        execution_results = []
        visited = set()
        queue = [(start_node, initial_data)]

        while queue:
            current_node, current_data = queue.pop(0)

            # Skip if already visited (to avoid cycles)
            if current_node.id in visited:
                continue
            visited.add(current_node.id)

            # Execute the current node
            try:
                output_data = self._execute_single_node(current_node, current_data)

                # Check if node execution returned an error
                if output_data.error:
                    execution_results.append(
                        {
                            "node_id": str(current_node.id),
                            "node_name": current_node.name,
                            "node_kind": current_node.kind,
                            "status": "error",
                            "error": output_data.error,
                            "data": output_data.json,
                        }
                    )
                    # Stop execution on error
                    break

                execution_results.append(
                    {
                        "node_id": str(current_node.id),
                        "node_name": current_node.name,
                        "node_kind": current_node.kind,
                        "status": "success",
                        "data": output_data.json,
                    }
                )

                # Find next nodes via edges
                next_edges = edge_map.get(current_node.id, [])
                for edge in next_edges:
                    target_node = node_map.get(edge.target_node_id)
                    if target_node and target_node.id not in visited:
                        queue.append((target_node, output_data))

            except Exception as e:
                execution_results.append(
                    {
                        "node_id": str(current_node.id),
                        "node_name": current_node.name,
                        "node_kind": current_node.kind,
                        "status": "error",
                        "error": str(e),
                    }
                )
                # Stop execution on error
                break

        return {
            "trigger_node_id": str(start_node.id),
            "trigger_node_name": start_node.name,
            "execution_results": execution_results,
        }

    def _execute_single_node(
        self, node: Node, input_data: ExecutionData
    ) -> ExecutionData:
        """
        Execute a single node.

        Args:
            node: The node to execute
            input_data: Input execution data

        Returns:
            ExecutionData: Output execution data

        Raises:
            ValueError: If node kind is not found
        """
        # Get the node definition by kind
        node_def = NODE_BY_ID.get(node.kind)
        if not node_def:
            raise ValueError(f"Node kind {node.kind} not found")

        # Create a new instance of the node type
        node_type_instance = node_def.description
        node_type_instance.parameters = node.parameters or {}

        # Execute the node
        try:
            output_data = node_type_instance.execute(input_data)
            return output_data
        except Exception as e:
            # Return error in execution data
            input_data.error = str(e)
            return input_data

    def _update_workflow_execution_status(
        self, workflow: Workflow, status: str, message: str
    ) -> None:
        """
        Update workflow execution status and timestamp.

        Args:
            workflow: The workflow to update
            status: Execution status
            message: Execution status message
        """
        workflow.last_execution_time = datetime.utcnow()
        workflow.execution_status = status
        workflow.execution_status_message = message
        self.db.commit()
        self.db.refresh(workflow)
