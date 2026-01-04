"""Command for triggering workflows based on received events."""

from uuid import UUID
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.models.node import Node
from app.models.event import Event
from app.services.workflow_service import WorkflowService
from app.services.node_service import NodeService
from app.commands.workflow.execute_workflow_command import ExecuteWorkflowCommand
from app.constants.node_kinds import NODE_BY_ID, CATEGORY_TRIGGER
from app.schemas.event import EventBase
from app.core.logging_config import get_logger
from app.nodes.event_received import EVENT_RECEIVED_NODE_ID

logger = get_logger("trigger_workflows_by_event")


class TriggerWorkflowsByEventCommand:
    """Command for triggering workflows based on received events."""

    def __init__(self, db: Session):
        """
        Initialize the trigger workflows by event command.

        Args:
            db: Database session
        """
        self.db = db
        self.workflow_service = WorkflowService(self.db)
        self.node_service = NodeService(self.db)

    def execute(self, event: Event) -> List[Dict[str, Any]]:
        """
        Find all active workflows with event triggers matching the event type and execute them.

        Args:
            event: The event that was received

        Returns:
            List of execution results for each matching workflow
        """
        logger.info(
            f"Searching for workflows triggered by event type: {event.event_type}"
        )

        # Get all active workflows
        active_workflows = self.workflow_service.get_active_workflows()
        logger.info(f"Found {len(active_workflows)} active workflows")

        matching_workflows = []
        for workflow in active_workflows:
            # Skip workflows without an active version
            if not workflow.active_version_id:
                continue

            # Check if this workflow has a matching event trigger
            if self._workflow_has_matching_event_trigger(workflow, event.event_type):
                matching_workflows.append(workflow)

        if not matching_workflows:
            logger.info(f"No workflows found matching event type: {event.event_type}")
            return []

        logger.info(
            f"Found {len(matching_workflows)} workflow(s) matching event type: {event.event_type}"
        )

        # Execute each matching workflow
        execution_results = []
        execute_command = ExecuteWorkflowCommand(self.db)

        # Convert event model to EventBase schema for passing to workflow
        # SQLAlchemy models return actual values when accessed on instances
        event_schema = EventBase(
            source=event.source,  # type: ignore[arg-type]
            spec_version=event.spec_version,  # type: ignore[arg-type]
            event_type=event.event_type,  # type: ignore[arg-type]
            event_data=event.event_data,  # type: ignore[arg-type]
            data_content_type=event.data_content_type,  # type: ignore[arg-type]
            subject=event.subject,  # type: ignore[arg-type]
            time=event.time,  # type: ignore[arg-type]
            tags=event.tags,  # type: ignore[arg-type]
            labels=event.labels,  # type: ignore[arg-type]
            privy=event.privy,  # type: ignore[arg-type]
            user_id=event.user_id,  # type: ignore[arg-type]
        )

        # Prepare initial data with event information (for backward compatibility)
        initial_data = {
            "event_type": event.event_type,
            "event_data": event.event_data,
        }

        for workflow in matching_workflows:
            try:
                logger.info(
                    f"Executing workflow {workflow.id} for event type: {event.event_type}"
                )
                result = execute_command.execute(
                    workflow_id=workflow.id,  # type: ignore[arg-type]
                    initial_data=initial_data,
                    manual=False,  # Use normal execution (will check is_active)
                    event=event_schema,  # Pass event to ExecutionData
                )
                execution_results.append(
                    {
                        "workflow_id": str(workflow.id),
                        "workflow_name": workflow.name,
                        "result": result,
                    }
                )
                logger.info(f"Successfully executed workflow {workflow.id}")
            except Exception as e:
                logger.error(
                    f"Error executing workflow {workflow.id} for event type {event.event_type}: {e}",
                    exc_info=True,
                )
                execution_results.append(
                    {
                        "workflow_id": str(workflow.id),
                        "workflow_name": workflow.name,
                        "error": str(e),
                    }
                )

        return execution_results

    def _workflow_has_matching_event_trigger(
        self, workflow: Workflow, event_type: str
    ) -> bool:
        """
        Check if a workflow has an event trigger node matching the given event type.

        Args:
            workflow: The workflow to check
            event_type: The event type to match

        Returns:
            bool: True if the workflow has a matching event trigger, False otherwise
        """
        if not workflow.active_version_id:
            return False

        # Query for event trigger nodes using node service, filtered by workflow version and kind
        event_trigger_nodes = self.node_service.get_nodes_by_workflow_version_and_kind(
            workflow_version_id=workflow.active_version_id,  # type: ignore[arg-type]
            kind=EVENT_RECEIVED_NODE_ID,
        )
        logger.info(f"Found {len(event_trigger_nodes)} event trigger nodes")

        # Check if any trigger node matches the event type
        for trigger_node in event_trigger_nodes:
            if self._node_matches_event_type(trigger_node, event_type):
                return True

        return False

    def _node_matches_event_type(self, node: Node, event_type: str) -> bool:
        """
        Check if an event trigger node matches the given event type.

        Event trigger nodes have their event_type stored in the properties field
        as a list of dicts, e.g., [{"event_type": "test_event"}].

        Args:
            node: The event trigger node to check
            event_type: The event type to match

        Returns:
            bool: True if the node matches the event type, False otherwise
        """
        if not node.parameters:
            return False

        logger.info(f"Node parameters: {node.parameters}")

        if node.parameters.get("event_type") == event_type:
            return True

        return False
