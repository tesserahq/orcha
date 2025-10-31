from fastapi import APIRouter

from app.schemas.common import ListResponse
from app.schemas.node_kind import CategoryWithNodes
from app.constants.node_kinds import NODE_CATEGORIES, NODE_KINDS_BY_CATEGORY


router = APIRouter(
    prefix="/nodes",
    tags=["nodes"],
    responses={404: {"description": "Not found"}},
)


@router.get("/categories", response_model=ListResponse[CategoryWithNodes])
def list_categories() -> ListResponse[CategoryWithNodes]:
    """Return all node categories with their associated node kinds."""
    categories = []
    for category_key, category_info in NODE_CATEGORIES.items():
        categories.append(
            CategoryWithNodes(
                key=category_info["key"],
                name=category_info["name"],
                description=category_info["description"],
                nodes=NODE_KINDS_BY_CATEGORY.get(category_key, []),
            )
        )
    return ListResponse(items=categories)
