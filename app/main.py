"""FastAPI main application entry point (Constitution Article IV.5, V.1, and VI)."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.logging_config import configurar_logging
from app.routers import usuarios, gastos
from app.mcp.server import mcp as mcp_server

configurar_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

mcp_app = mcp_server.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing background services and MCP session manager."""
    try:
        async with mcp_server.session_manager.run():
            yield
    finally:
        mcp_server.session_manager._has_started = False



app = FastAPI(title="API de Control de Gastos", lifespan=lifespan)
app.include_router(usuarios.router)
app.include_router(gastos.router)
app.mount("/mcp", mcp_app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware logging HTTP request duration and status."""
    inicio = time.perf_counter()
    response = await call_next(request)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    logger.info(
        "%s %s -> %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duracion_ms,
    )
    return response


@app.exception_handler(Exception)
async def manejar_error_no_controlado(request: Request, exc: Exception):
    """Global exception handler returning 500 without leaking stack traces (Constitution Article IV.5)."""
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})
