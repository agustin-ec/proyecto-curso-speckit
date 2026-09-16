"""FastAPI application entry point (Constitution Article IV.5 and V.1)."""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import usuarios, gastos

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Control de Gastos API",
    description="API para el sistema de control de gastos personales",
    version="0.1.0",
)

app.include_router(usuarios.router)
app.include_router(gastos.router)


@app.exception_handler(Exception)
async def manejar_error_no_controlado(request: Request, exc: Exception):
    """Global exception handler returning status 500 without leaking stack traces (Constitution Article IV.5)."""
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})
