# Technical Research: Sistema de Control de Gastos Personales

**Feature**: [`specs/001-control-gastos/spec.md`](../spec.md)  
**Date**: 2026-09-15  
**Status**: Resolved / Completed

Este documento consolida las decisiones de arquitectura, tecnologías y dependencias para la implementación del sistema, garantizando trazabilidad absoluta con la Constitución del Proyecto (`.specify/memory/constitution.md`).

---

## 1. Web Framework & Servidor ASGI

- **Decisión**: FastAPI con `uvicorn[standard]`
- **Rationale**: 
  - FastAPI ofrece soporte nativo para ASGI, validación de esquemas con Pydantic v2, generación automática de OpenAPI y sistema de inyección de dependencias (`Depends`), ideal para acoplar `get_db`, `get_current_user` y el montaje de endpoints y servidores MCP en el mismo proceso.
  - `uvicorn[standard]` proporciona un servidor ASGI de alto rendimiento con soporte uvloop y websockets.
- **Alternativas consideradas**:
  - *Flask*: Descartado por requerir extensiones de terceros para validación Pydantic, OpenAPI y no ser nativamente asíncrono.
  - *Django Ninja*: Descartado por añadir overhead innecesario del ORM de Django cuando el estándar del proyecto es SQLAlchemy y FastAPI puro.

---

## 2. Persistencia y Migraciones

- **Decisión**: SQLAlchemy 2.0 + Alembic (SQLite en desarrollo/test, interoperable con PostgreSQL)
- **Rationale**: 
  - Cumple directamente con el **Artículo III.1 y III.2**.
  - Permite configurar `connect_args={"check_same_thread": False}` condicionalmente para SQLite sin alterar modelos ni repositorios.
  - Alembic gestiona el historial de migraciones de base de datos de manera determinista y reproducible.
- **Alternativas consideradas**:
  - *SQLAlchemy puro sin Alembic (`Base.metadata.create_all`)*: Válido para tests rápidos en memoria, pero insuficiente para entornos productivos y evoluciones de esquema. Alembic se incluye formalmente para la gestión de migraciones.
  - *SQL crudo / SQLite3 driver directo*: Descartado expresamente por el Artículo III.1 (prohibido SQL crudo concatenado).

---

## 3. Seguridad: Autenticación, JWT y Hashing

- **Decisión**: 
  - JWT: `pyjwt` (con algoritmo HS256).
  - Password Hashing: `passlib[bcrypt]` con fijación estricta de `bcrypt<4.1`.
  - Configuración: `pydantic-settings` leyendo `.env`.
  - Dependencias de validación/auth: `email-validator` y `python-multipart`.
- **Rationale**: 
  - **Artículo IV.1**: Passlib maneja de manera estándar y segura el hash de contraseñas mediante bcrypt. La fijación `bcrypt<4.1` es obligatoria porque las versiones >=4.1 de bcrypt introdujeron cambios incompatibles en su API interna de C que rompen `passlib 1.7.4` en tiempo de ejecución.
  - **Artículo IV.2 y IV.3**: Se adopta `pyjwt` como biblioteca única y canónica para codificación y decodificación de tokens JWT firmados con HS256 y expiración finita (`ACCESS_TOKEN_EXPIRE_MINUTES`). Se rechaza `python-jose` por encontrarse en estado de abandono sin mantenimiento activo.
  - `pydantic-settings` asegura la carga tipada de `SECRET_KEY` y `DATABASE_URL` desde `.env`.
  - `email-validator` es requerido por Pydantic para el tipo `EmailStr`.
  - `python-multipart` es obligatorio para que FastAPI procese el payload de `OAuth2PasswordRequestForm` en el endpoint `/usuarios/token`.
- **Alternativas consideradas**:
  - *python-jose*: Descartado por falta de mantenimiento y vulnerabilidades latentes.
  - *argon2-cffi*: Descartado para mantener compatibilidad exacta con los tests de referencia de las Sesiones 6-8 que asumen hashes compatibles con bcrypt.

---

## 4. Arquitectura en Capas e Inyección de Dependencias (DIP)

- **Decisión**: Paquetes Python independientes bajo `app/` (`routers/`, `services/`, `repositories/`, `utils/`, `mcp/tools/`, `models/`, `schemas/`), aplicando DIP mediante parámetros con valor por defecto.
- **Rationale**: 
  - **Artículo I**: Flujo unidireccional estricto: `routers/` → `services/` → `repositories/`. Los routers manejan HTTP; los services contienen 100% de la lógica de negocio; los repositories manejan persistencia; `utils/` son funciones puras.
  - **Artículo II.3**: En `services/gastos.py`, la inyección se implementa mediante la firma:
    ```python
    def registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict:
        ...
    ```
    Esto permite inyectar un repositorio falso (`RepositorioFalso`) en tests unitarios sin recurrir a contenedores IoC externos complejos ni a `unittest.mock` (prohibido por el Artículo VII.2).
- **Alternativas consideradas**:
  - *python-dependency-injector*: Descartado por sobreingeniería y complejidad artificial para un proyecto backend conciso.
  - *Clases con constructores e interfaces abstractas*: Descartado conforme al Artículo II.4 y VIII.2 (los repositorios son módulos con funciones sueltas para compatibilidad con las Sesiones 6-8).

---

## 5. Integración con Model Context Protocol (MCP)

- **Decisión**: SDK oficial `mcp` (`mcp[cli]` / `mcp`) montado dentro de FastAPI usando el transporte `streamable-http`, delegando en `services/`.
- **Rationale**: 
  - **Artículo VI**: Cada herramienta (`registrar_gasto`, `listar_gastos`) es una función delgada que invoca directamente a `services.gastos`.
  - Los errores de negocio se capturan y retornan estructurados como `{"error": "..."}` para evitar abortos imprevistos de la sesión MCP.
  - En `streamable-http`, la identidad del usuario se resuelve extrayendo y verificando el token Bearer del header `Authorization` de la petición HTTP que establece el stream MCP.
  - Se define soporte para transporte `stdio` documentando explícitamente el uso del usuario demo configurado en variables de entorno como mecanismo de fallback.
- **Alternativas consideradas**:
  - *Proceso MCP independiente separado de FastAPI*: Descartado; montar MCP vía ASGI/streamable-http dentro de la misma aplicación FastAPI permite compartir el ciclo de vida, la configuración de base de datos y la autenticación sin duplicar código.

---

## 6. Estrategia de Pruebas y Cobertura

- **Decisión**: `pytest`, `pytest-cov`, `httpx` (para `starlette.testclient.TestClient`).
- **Rationale**: 
  - **Artículo VII.1**: Pirámide de pruebas (Unitarios > Integración > API).
  - **Unitarios (`test_gastos.py`)**: Validan el 100% de las reglas de negocio en `services/gastos.py` usando `RepositorioFalso` en memoria.
  - **Integración (`test_integracion_gastos.py`)**: Validan operaciones contra una base de datos real SQLite en memoria (`sqlite:///:memory:`).
  - **API (`test_api_gastos.py`)**: Usan `TestClient` con `app.dependency_overrides` para sustituir `get_db`, `get_gastos_repo` y `get_current_user`.
  - **Cobertura (Artículo VII.3)**: 
    - 100% cobertura de reglas de negocio explícitas.
    - ≥90% en `services/`.
    - ≥80% en `services/ + repositories/ + routers/ + utils/`.
    - Exclusión explícita en `pyproject.toml` de archivos de infraestructura de arranque (`main.py`, `mcp/server.py`, `mcp/auth.py`, `logging_config.py`).
- **Alternativas consideradas**:
  - *unittest estándar*: Descartado en favor de las fixtures idiomáticas y plugins de `pytest`.
