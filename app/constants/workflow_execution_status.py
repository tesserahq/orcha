"""Workflow execution status constants.

Provides centralized constants for workflow execution statuses to ensure
consistency across the application.
"""


class WorkflowExecutionStatus:
    """Constants for workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
