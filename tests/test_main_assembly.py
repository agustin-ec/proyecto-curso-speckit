"""Tests for app/main.py assembly (Constitution Article IV.5, V, and VI)."""

from starlette.testclient import TestClient
from app.main import app


def test_main_app_structure_and_routes():
    """Verify app assembly includes expected routers and mounts."""
    openapi_paths = list(app.openapi()["paths"].keys())

    # Verify routers included
    assert "/usuarios/" in openapi_paths
    assert "/usuarios/token" in openapi_paths
    assert "/gastos/" in openapi_paths

    # Verify MCP mount exists
    mount_paths = [r.path for r in app.routes if hasattr(r, "path")]
    assert "/mcp" in mount_paths



def test_main_app_global_exception_handler():
    """Verify global exception handler catches unhandled Exception and returns 500 without stacktrace."""
    from fastapi import APIRouter

    test_router = APIRouter()

    @test_router.get("/test-500-error")
    def fail():
        raise RuntimeError("Fallo catastrófico simulado")

    app.include_router(test_router)

    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/test-500-error")
        assert resp.status_code == 500
        assert resp.json() == {"detail": "Error interno del servidor"}
