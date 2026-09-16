"""Expense management router (Constitution Article III.3, V.1, and VIII.1)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_gastos_repo
from app.models.usuario import Usuario
from app.schemas.gasto import GastoCreate, GastoOut
from app.services import gastos as gastos_service
from app.services.gastos import CategoriaInvalidaError, LimiteExcedidoError

router = APIRouter(prefix="/gastos", tags=["gastos"])


@router.post("/", response_model=GastoOut, status_code=status.HTTP_201_CREATED)
def crear_gasto(
    datos: GastoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
    repo=Depends(get_gastos_repo),
) -> dict:
    """Register a new expense for the authenticated user."""
    try:
        return gastos_service.registrar_gasto(
            db,
            usuario_actual.id,
            datos.descripcion,
            datos.monto,
            datos.categoria,
            repo=repo,
        )
    except (ValueError, CategoriaInvalidaError, LimiteExcedidoError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[GastoOut])
def listar_gastos(
    skip: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=20, gt=0, le=100, description="Número máximo de registros a obtener"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
    repo=Depends(get_gastos_repo),
) -> list[dict]:
    """List expenses for authenticated user with pagination."""
    return gastos_service.listar_gastos(
        db, usuario_actual.id, skip=skip, limit=limit, repo=repo
    )

