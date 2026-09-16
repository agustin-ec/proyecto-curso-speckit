"""MCP expense management tools (Constitution Article VI.1, VI.2, VI.3, and VI.4)."""

from mcp.server.fastmcp import FastMCP
from mcp.server.auth.middleware.auth_context import get_access_token

from app.core.config import settings
from app.database import SessionLocal
from app.repositories import usuarios as usuarios_repository
from app.services import gastos as gastos_service
from app.core.security import get_password_hash


def _obtener_o_crear_usuario_demo(db):
    """Retrieve or create the demo user for stdio transport (Constitution Article VI.4)."""
    usuario = usuarios_repository.obtener_por_email(db, settings.DEMO_USER_EMAIL)
    if usuario is None:
        usuario = usuarios_repository.guardar(
            db, settings.DEMO_USER_EMAIL, get_password_hash(settings.MCP_DEMO_PASSWORD)
        )
    return usuario


def _resolver_usuario_actual(db):
    """Resolve the authenticated user from the active MCP access token or fallback to demo."""
    access_token = get_access_token()
    if access_token is None:
        # stdio transport fallback
        return _obtener_o_crear_usuario_demo(db)

    usuario = None
    if access_token.subject:
        usuario = usuarios_repository.obtener_por_email(db, access_token.subject)
    if usuario is None:
        raise ValueError("El token no corresponde a ningún usuario registrado")
    return usuario


def registrar_gasto(descripcion: str, monto: float, categoria: str) -> dict:
    """Registra un nuevo gasto. Usar cuando el usuario mencione una compra o pago que quiere trackear."""
    db = SessionLocal()
    try:
        usuario = _resolver_usuario_actual(db)
        return gastos_service.registrar_gasto(db, usuario.id, descripcion, monto, categoria)
    except (ValueError, gastos_service.CategoriaInvalidaError, gastos_service.LimiteExcedidoError) as e:
        return {"error": str(e)}
    finally:
        db.close()


def listar_gastos(skip: int = 0, limit: int = 20) -> list[dict]:
    """Lista todos los gastos registrados del usuario. Usar cuando pregunten por sus gastos o quieran un resumen."""
    db = SessionLocal()
    try:
        usuario = _resolver_usuario_actual(db)
        return gastos_service.listar_gastos(db, usuario.id, skip=skip, limit=limit)
    finally:
        db.close()


def register(mcp: FastMCP) -> None:
    """Register expense tools on the FastMCP server instance."""
    mcp.tool()(registrar_gasto)
    mcp.tool()(listar_gastos)
