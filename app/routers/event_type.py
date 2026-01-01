from typing import Optional
from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel

from app.schemas.common import ListResponse
from app.tasks.backfill_event_types_task import backfill_event_types_task
from app.utils.event_type_cache import get_event_types
from app.auth.rbac import build_rbac_dependencies


async def infer_domain(request: Request) -> Optional[str]:
    return "*"


RESOURCE = "event_type"
rbac = build_rbac_dependencies(
    resource=RESOURCE,
    domain_resolver=infer_domain,
)

router = APIRouter(
    prefix="/event-types",
    tags=["event-types"],
    responses={404: {"description": "Not found"}},
)


class BackfillResponse(BaseModel):
    """Response model for backfill task trigger."""

    message: str
    task_triggered: bool = True


@router.get("", response_model=ListResponse[str])
def list_event_types(
    _authorized: bool = Depends(rbac["read"]),
) -> ListResponse[str]:
    """Get the list of all registered event types from cache."""
    event_types = get_event_types()
    event_types.sort()
    return ListResponse(items=event_types)


@router.post("", response_model=BackfillResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_backfill(_authorized: bool = Depends(rbac["create"])) -> BackfillResponse:
    """Trigger the backfill task to populate event types cache from database."""
    backfill_event_types_task.delay()
    return BackfillResponse(message="Backfill task triggered successfully")
