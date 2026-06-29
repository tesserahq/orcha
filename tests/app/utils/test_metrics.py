import pytest
from fastapi import FastAPI, APIRouter
from starlette.routing import Match
from starlette.testclient import TestClient

from app.utils.metrics import PrometheusMiddleware


def _make_request(app: FastAPI, path: str, method: str = "GET"):
    """Build a minimal scope dict and return a Starlette Request."""
    from starlette.requests import Request
    from starlette.datastructures import Headers

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": b"",
        "headers": [],
        "app": app,
    }
    return Request(scope)


@pytest.fixture()
def app_with_included_router():
    """App that has an included sub-router, producing _IncludedRouter entries in app.routes."""
    app = FastAPI()
    router = APIRouter(prefix="/items")

    @router.get("/{item_id}")
    def get_item(item_id: int):
        return {"id": item_id}

    app.include_router(router)
    return app


def test_get_path_returns_path_for_known_route(app_with_included_router):
    request = _make_request(app_with_included_router, "/items/42")
    path, is_handled = PrometheusMiddleware.get_path(request)
    assert is_handled is True
    assert path == "/items/{item_id}"


def test_get_path_falls_back_for_unknown_route(app_with_included_router):
    request = _make_request(app_with_included_router, "/no/such/route")
    path, is_handled = PrometheusMiddleware.get_path(request)
    assert is_handled is False
    assert path == "/no/such/route"


def test_get_path_does_not_crash_with_included_router(app_with_included_router):
    """Regression: _IncludedRouter has no .path — get_path must not raise AttributeError."""
    has_routerless_entry = any(
        not hasattr(r, "path") for r in app_with_included_router.routes
    )
    assert has_routerless_entry, "Fixture should produce a route without .path"

    request = _make_request(app_with_included_router, "/items/1")
    path, is_handled = PrometheusMiddleware.get_path(request)
    assert path is not None
