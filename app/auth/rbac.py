# app/auth/rbac.py

from typing import Awaitable, Callable, Optional
from fastapi import Request
from tessera_sdk.utils.authorization_dependency import authorize
from app.constants.rbac_actions import RBACActions

DomainResolver = Callable[[Request], Awaitable[Optional[str]]]


def build_rbac_dependencies(
    *,
    resource: str,
    domain_resolver: DomainResolver,
):
    return {
        "create": authorize(
            resource=resource,
            action=RBACActions.CREATE,
            domain_resolver=domain_resolver,
        ),
        "read": authorize(
            resource=resource,
            action=RBACActions.READ,
            domain_resolver=domain_resolver,
        ),
        "update": authorize(
            resource=resource,
            action=RBACActions.UPDATE,
            domain_resolver=domain_resolver,
        ),
        "delete": authorize(
            resource=resource,
            action=RBACActions.DELETE,
            domain_resolver=domain_resolver,
        ),
    }
