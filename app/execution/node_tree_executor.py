"""BFS graph executor for workflow node trees."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional
from uuid import UUID

from app.constants.node_types import ExecutionContext, ExecutionData, NodeResult
from app.models.edge import Edge
from app.models.node import Node

NodeExecutorFn = Callable[[Node, ExecutionContext], ExecutionData]


class NodeTreeExecutor:
    """Executes a BFS-ordered node graph against an ExecutionContext.

    All traversal mechanics — adjacency maps, visited tracking, input
    snapshotting, NodeResult assembly, and error dispatch — are encapsulated
    here. The caller owns context construction, DB loading, and persistence.

    The node execution callable is injected at construction time, keeping this
    class free of NODE_BY_ID and any ORM/session concerns.
    """

    def __init__(self, execute_node: NodeExecutorFn) -> None:
        self._execute_node = execute_node

    def run(
        self,
        start_node: Node,
        nodes: List[Node],
        edges: List[Edge],
        context: ExecutionContext,
    ) -> Optional[str]:
        """Execute the graph from start_node via BFS.

        Returns None on full success, or an error string describing the first
        failure. Mutates context in place by appending NodeResult entries.
        Failed nodes are not recorded in the context.
        """
        node_map: Dict[UUID, Node] = {node.id: node for node in nodes}

        edge_map: Dict[UUID, List[Edge]] = {}
        for edge in edges:
            edge_map.setdefault(edge.source_node_id, []).append(edge)

        visited: set = set()
        queue = [start_node]

        while queue:
            current_node = queue.pop(0)

            if current_node.id in visited:
                continue
            visited.add(current_node.id)

            input_snapshot = dict(context.get_previous_output().json)

            try:
                output_data = self._execute_node(current_node, context)

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
