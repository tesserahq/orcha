from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.schemas.user import User
from app.services.user_service import UserService
from app.auth.rbac import build_rbac_dependencies


async def infer_domain(request: Request) -> Optional[str]:
    return "*"


RESOURCE = "user"
rbac = build_rbac_dependencies(
    resource=RESOURCE,
    domain_resolver=infer_domain,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["read"]),
):
    """Get a user by ID."""
    user = UserService(db).get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
