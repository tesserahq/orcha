"""Command for executing a workflow."""

import copy
import uuid
from uuid import UUID
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.workflow import Workflow
from app.models.node import Node
from app.models.edge import Edge
from app.models.workflow_execution import WorkflowExecution
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.node_repository import NodeRepository
from app.repositories.edge_repository import EdgeRepository
from app.repositories.workflow_execution_repository import WorkflowExecutionRepository
from app.constants.node_kinds import NODE_BY_ID, CATEGORY_TRIGGER
from app.constants.node_types import ExecutionContext, ExecutionData, NodeResult
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
        self.workflow_repository = WorkflowRepository(self.db)
        self.node_repository = NodeRepository(self.db)
        self.edge_repository = EdgeRepository(self.db)
        self.execution_repository = WorkflowExecutionRepository(self.db)

    def execute(
        self,
        workflow_id: UUID,
        initial_data: Optional[Dict[str, Any]] = None,
        manual: bool = False,
        event: Optional[EventBase] = None,
        triggered_by: str = "manual",
    ) -> Dict[str, Any]:
        """Execute a workflow.

        The workflow will only run if is_active=True or manual=True.

        Args:
            workflow_id: The ID of the workflow to execute
            initial_data: Data passed by the caller (used as trigger_event for manual runs)
            manual: Whether this is a manual execution (bypasses is_active check)
            event: Event schema for event-triggered runs
            triggered_by: Source of the execution ("manual" or "event")

        Returns:
            Serialized ExecutionContext dict with workflow_id, status, and error_message

        Raises:
            ResourceNotFoundError: If workflow is not found
            ValueError: If workflow cannot be executed
        """
        workflow = self.workflow_repository.get_workflow(workflow_id)
        if not workflow:
            raise ResourceNotFoundError(f"Workflow with id {workflow_id} not found")

        if not workflow.is_active and not manual:
            raise ValueError(
                f"Workflow {workflow_id} is not active and manual execution was not requested"
            )

        if not workflow.active_version_id:
            raise ValueError(f"Workflow {workflow_id} has no active version")

        workflow_version_id = workflow.active_version_id

        nodes = self.node_repository.get_nodes_by_workflow_version(workflow_version_id)
        if not nodes:
            raise ValueError(f"Workflow version {workflow_version_id} has no nodes")

        edges = self.edge_repository.get_edges_by_workflow_version(workflow_version_id)

        trigger_nodes = self._find_trigger_nodes(nodes)
        if not trigger_nodes:
            raise ValueError(
                f"Workflow version {workflow_version_id} has no trigger nodes"
            )
        if len(trigger_nodes) > 1:
            raise ValueError(
                f"Workflow version {workflow_version_id} has more than one trigger node"
            )

        trigger_node = trigger_nodes[0]

        # For event-triggered runs, trigger_event is the raw CloudEvents payload.
        # For manual runs, it is the caller-supplied initial_data (or empty dict).
        trigger_event = event.model_dump() if event else (initial_data or {})

        execution_id = uuid.uuid4()
        context = ExecutionContext(
            trigger_event=trigger_event,
            execution_id=str(execution_id),
            triggered_by=triggered_by,
        )

        started_at = datetime.now(timezone.utc)
        error_message = self._execute_node_tree(trigger_node, nodes, edges, context)
        finished_at = datetime.now(timezone.utc)

        status = "error" if error_message else "completed"
        full_result = {
            "workflow_id": str(workflow_id),
            "status": status,
            "error_message": error_message,
            **context.to_dict(),
        }

        self.execution_repository.create_execution(
            WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                workflow_version_id=workflow_version_id,
                status=status,
                triggered_by=triggered_by,
                started_at=started_at,
                finished_at=finished_at,
                result=full_result,
                error_message=error_message,
            )
        )

        self._update_workflow_execution_status(
            workflow,
            status,
            (
                "Workflow execution completed with errors"
                if error_message
                else "Workflow executed successfully"
            ),
        )

        return full_result

    def _find_trigger_nodes(self, nodes: List[Node]) -> List[Node]:
        trigger_nodes = []
        for node in nodes:
            node_def = NODE_BY_ID.get(node.kind)
            if node_def is None:
                raise ValueError(f"Node kind {node.kind} not found")
            if node_def.category == CATEGORY_TRIGGER:
                trigger_nodes.append(node)
        return trigger_nodes

    def _execute_node_tree(
        self,
        start_node: Node,
        all_nodes: List[Node],
        all_edges: List[Edge],
        context: ExecutionContext,
    ) -> Optional[str]:
        """Execute nodes via BFS starting from the trigger node.

        Returns an error message string if any node fails, or None on success.
        Failed nodes are not recorded in the context.
        """
        node_map = {node.id: node for node in all_nodes}

        edge_map: Dict[UUID, List[Edge]] = {}
        for edge in all_edges:
            if edge.source_node_id not in edge_map:
                edge_map[edge.source_node_id] = []
            edge_map[edge.source_node_id].append(edge)

        visited = set()
        queue = [start_node]

        while queue:
            current_node = queue.pop(0)

            if current_node.id in visited:
                continue
            visited.add(current_node.id)

            input_snapshot = dict(context.get_previous_output().json)

            try:
                output_data = self._execute_single_node(current_node, context)

                if output_data.error:
                    return f"{current_node.name}: {output_data.error}"

                context.append_result(
                    NodeResult(
                        node_id=str(current_node.id),
                        node_name=current_node.name,
                        node_kind=current_node.kind,
                        status="success",
                        input=input_snapshot,
                        output=output_data.json,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                )

                for edge in edge_map.get(current_node.id, []):
                    target_node = node_map.get(edge.target_node_id)
                    if target_node and target_node.id not in visited:
                        queue.append(target_node)

            except Exception as e:
                return f"{current_node.name}: {str(e)}"

        return None

    def _execute_single_node(
        self, node: Node, context: ExecutionContext
    ) -> ExecutionData:
        """Execute a single node against the current execution context.

        Copies the node description to avoid mutating the global singleton in
        NODE_BY_ID — concurrent executions of the same kind would otherwise
        overwrite each other's parameters.
        """
        node_def = NODE_BY_ID.get(node.kind)
        if not node_def:
            raise ValueError(f"Node kind {node.kind} not found")

        node_type_instance = copy.copy(node_def.description)
        node_type_instance.parameters = node.parameters or {}

        try:
            return node_type_instance.execute(context)
        except Exception as e:
            return ExecutionData(json=context.get_previous_output().json, error=str(e))

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
        workflow.last_execution_time = datetime.now(timezone.utc)
        workflow.execution_status = status
        workflow.execution_status_message = message
        self.db.commit()
        self.db.refresh(workflow)
