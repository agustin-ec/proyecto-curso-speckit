# Interface Contract: Compatibility Contract (Sesiones 6-8)

**Feature**: [`specs/001-control-gastos/spec.md`](../spec.md)  
**Date**: 2026-09-15  
**Status**: Mandatory / Non-Negotiable (Constitution Article VIII)

Este documento fija de manera inalterable las firmas, módulos, funciones y excepciones requeridas por la suite de pruebas preexistente (`test_gastos.py`, `test_integracion_gastos.py`, `test_api_gastos.py`). Ninguna tarea de implementación ni refactorización puede renombrar, reordenar o eliminar los símbolos aquí declarados.

---

## 1. Módulo `app/services/gastos.py`

### Constantes y Excepciones
- `LIMITE_POR_CATEGORIA: float = 500.0`
- `class CategoriaInvalidaError(Exception): pass`
- `class LimiteExcedidoError(Exception): pass`

### Firmas de Funciones
```python
def registrar_gasto(
    db,
    usuario_id: int,
    descripcion: str,
    monto: float,
    categoria: str,
    repo=gastos_repository
) -> dict:
    """
    Registra un gasto validando reglas de negocio:
    - monto > 0
    - descripcion no vacía
    - categoria pertenece a categorías válidas (lanza CategoriaInvalidaError)
    - acumulado + monto <= LIMITE_POR_CATEGORIA (lanza LimiteExcedidoError si es estrictamente mayor a 500.0)
    Inyecta el repositorio a través del parámetro keyword 'repo'.
    """
    ...

def listar_gastos(
    db,
    usuario_id: int,
    skip: int = 0,
    limit: int = 20,
    repo=gastos_repository
) -> list[dict]:
    """
    Retorna la lista de gastos del usuario indicado con paginación.
    Inyecta el repositorio a través del parámetro keyword 'repo'.
    """
    ...
```

---

## 2. Módulo `app/repositories/gastos.py`

**Formato obligatorio**: Módulo Python con funciones sueltas (**NO** una clase). Retorna tipos primitivos (`dict`, `list[dict]`, `float`), nunca objetos ORM o sesiones directas.

```python
def guardar(db, usuario_id: int, descripcion: str, monto: float, categoria: str) -> dict:
    """Inserta el registro de gasto y devuelve un dict representativo."""
    ...

def listar(db, usuario_id: int, skip: int = 0, limit: int = 20) -> list[dict]:
    """Devuelve la lista paginada de gastos para el usuario_id."""
    ...

def total_por_categoria(db, usuario_id: int, categoria: str) -> float:
    """Calcula la suma acumulada de montos para el usuario y categoría dados (retorna 0.0 si no hay gastos)."""
    ...
```

---

## 3. Módulo `app/repositories/usuarios.py`

```python
def obtener_por_email(db, email: str) -> Usuario | None:
    """Recupera el objeto Usuario correspondiente al email o None."""
    ...

def guardar(db, email: str, hashed_password: str) -> Usuario:
    """Persiste un nuevo usuario con la contraseña ya hasheada y retorna el objeto Usuario."""
    ...
```

---

## 4. Dependencias y Modelos Requeridos

Los siguientes símbolos son importados directamente por los tests copiados:
- `app.database.get_db`: Generador que yield-ea la sesión de SQLAlchemy.
- `app.dependencies.get_current_user`: Dependencia FastAPI que valida el token Bearer y entrega la entidad del usuario.
- `app.dependencies.get_gastos_repo`: Dependencia que provee el módulo `app.repositories.gastos`.
- `app.models.usuario.Usuario`: Clase del modelo con constructor que acepta `(id=..., email=..., hashed_password=...)`.

---

## 5. Módulo `tests/__init__.py` y `RepositorioFalso`

- El archivo `tests/__init__.py` DEBE existir en la raíz del paquete de tests.
- `tests/test_gastos.py` DEBE definir la clase `RepositorioFalso` que emula el contrato de `app/repositories/gastos.py` en memoria para que `test_api_gastos.py` pueda importarla mediante:
  ```python
  from tests.test_gastos import RepositorioFalso
  ```
