from app.commands.update_workflow_command import UpdateWorkflowCommand
from app.schemas.workflow import WorkflowUpdateRequest


def test_update_workflow_command_updates_fields(db, test_workflow):
    command = UpdateWorkflowCommand(db)
    payload = WorkflowUpdateRequest(
        name="Updated Workflow Name",
        description="Updated description",
        is_active=False,
    )

    updated = command.execute(test_workflow.id, payload)

    assert updated is not None
    assert updated.id == test_workflow.id
    assert updated.name == payload.name
    assert updated.description == payload.description
    assert updated.is_active is False
