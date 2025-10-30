from fastapi import APIRouter

from app.schemas.common import ListResponse
from app.schemas.node_kind import NodeKind as NodeKindSchema
from app.constants.node_kinds import NODE_KINDS


router = APIRouter(
    prefix="/nodes",
    tags=["nodes"],
    responses={404: {"description": "Not found"}},
)


@router.get("/kinds", response_model=ListResponse[NodeKindSchema])
def list_node_kinds() -> ListResponse[NodeKindSchema]:
    """Return all available node kinds."""
    return ListResponse(data=NODE_KINDS)  # type: ignore[arg-type]
