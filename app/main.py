"""FastAPI application entry point."""

from fastapi import FastAPI
from app.routers import usuarios

app = FastAPI(
    title="Control de Gastos API",
    description="API para el sistema de control de gastos personales",
    version="0.1.0",
)

app.include_router(usuarios.router)
