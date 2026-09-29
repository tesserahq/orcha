"""Event-triggered workflows under the managed transaction boundary.

Workflow nodes can have external effects (HTTP requests, emails), so each
triggered workflow is committed as soon as it finishes, and a workflow
failure never loses the stored event.
"""

import importlib
from unittest.mock import Mock

import pytest

from app.commands.workflow.execute_workflow_command import ExecuteWorkflowCommand
from app.commands.workflow.trigger_workflows_by_event_command import (
    TriggerWorkflowsByEventCommand,
)
from app.models.event import Event
from app.models.workflow import Workflow

nats_task = importlib.import_module("app.tasks.process_nats_event_task")


@pytest.fixture
def two_triggered_workflows(db, test_workflow, setup_workflow, test_workflow_version):
    for workflow in (test_workflow, setup_workflow):
        workflow.active_version_id = test_workflow_version.id
        workflow.execution_status = None
    db.flush()
    return test_workflow, setup_workflow


def _trigger_command(db, workflows, monkeypatch, failing_id):
    command = TriggerWorkflowsByEventCommand(db)
    monkeypatch.setattr(
        command.workflow_repository,
        "get_active_workflows",
        Mock(return_value=list(workflows)),
    )
    monkeypatch.setattr(
        command, "_workflow_has_matching_event_trigger", Mock(return_value=True)
    )

    def execute(self, workflow_id, **kwargs):
        workflow = self.db.get(Workflow, workflow_id)
        workflow.execution_status = "ran"
        self.db.flush()
        if workflow_id == failing_id:
            raise RuntimeError("node failed")
        return {"status": "completed"}

    monkeypatch.setattr(ExecuteWorkflowCommand, "execute", execute)
    return command


def test_each_workflow_commits_independently(
    db, execution_boundary, setup_event, two_triggered_workflows, monkeypatch
):
    failing, succeeding = two_triggered_workflows
    command = _trigger_command(
        db, two_triggered_workflows, monkeypatch, failing_id=failing.id
    )

    with pytest.raises(RuntimeError, match="later failure"):
        with execution_boundary():
            results = command.execute(setup_event)
            raise RuntimeError("later failure")

    assert [bool(r.get("error")) for r in results] == [True, False]
    db.expire_all()
    # The failing workflow was rolled back to its savepoint; the successful
    # one was checkpointed and survives the later rollback.
    assert db.get(Workflow, failing.id).execution_status is None
    assert db.get(Workflow, succeeding.id).execution_status == "ran"


def test_workflow_failure_keeps_the_event(db, execution_boundary, monkeypatch, faker):
    monkeypatch.setattr(nats_task, "session_scope", execution_boundary)
    monkeypatch.setattr(
        TriggerWorkflowsByEventCommand,
        "execute",
        Mock(side_effect=RuntimeError("trigger failed")),
    )
    monkeypatch.setattr(nats_task, "add_event_type", Mock())
    subject = f"subject-{faker.uuid4()}"

    event_id = nats_task.process_nats_event_task(
        {"source": "tests", "event_type": "thing.happened", "subject": subject}
    )

    assert event_id is not None
    assert db.query(Event).filter(Event.subject == subject).count() == 1
