# Implementation Plan: Sistema de Control de Gastos Personales

**Branch**: `001-control-gastos` | **Date**: 2026-09-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-control-gastos/spec.md`

---

## Summary

Implementar un backend robusto y modular para el **Sistema de Control de Gastos Personales** que expone una API REST moderna con FastAPI y una interfaz de herramientas agénticas mediante el SDK oficial de **Model Context Protocol (MCP)** sobre transporte `streamable-http`. La solución aplica una arquitectura limpia en capas estricta (`routers/` → `services/` → `repositories/` → `utils/`), inyección de dependencias por parámetro por defecto (DIP) para aislar la lógica de negocio sin `unittest.mock`, persistencia relacional con SQLAlchemy 2.0 y Alembic, seguridad con `pyjwt` (HS256) y `passlib[bcrypt]` (`bcrypt<4.1`), y compatibilidad innegociable con la suite de pruebas preexistente de las Sesiones 6-8.

---

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**:
  - `fastapi`: Framework web y ASGI
  - `uvicorn[standard]`: Servidor ASGI de alto rendimiento
  - `sqlalchemy>=2.0`: ORM relacional y capa de abstracción de base de datos
  - `alembic`: Control y ejecución de migraciones de base de datos
  - `pyjwt`: Codificación y verificación estricta de tokens JWT (HS256)
  - `passlib[bcrypt]`: Hashing criptográfico de contraseñas
  - `bcrypt<4.1`: Fijación estricta para garantizar compatibilidad binaria en tiempo de ejecución con `passlib 1.7.4`
  - `pydantic-settings`: Carga tipada y validación de variables de entorno desde `.env`
  - `email-validator`: Validación estándar de formato de correo electrónico para `EmailStr`
  - `python-multipart`: Soporte de formularios `application/x-www-form-urlencoded` para OAuth2 Password Flow
  - `mcp`: SDK oficial de Model Context Protocol
  - `pytest`, `pytest-cov`, `httpx`: Suite de pruebas y cliente de test para FastAPI
- **Storage**: SQLite para desarrollo local y ejecución de tests en memoria (`sqlite:///:memory:`), totalmente interoperable con PostgreSQL mediante SQLAlchemy sin tocar capas de servicios ni controladores.
- **Testing**: `pytest` con plugins `pytest-cov` y `httpx`.
- **Target Platform**: Servidor Linux / Contenedor Docker / Entorno POSIX local.
- **Project Type**: Servicio web REST API con servidor de herramientas MCP integrado.
- **Performance Goals**: Latencia inferior a 50ms para operaciones CRUD de gastos en entorno local; tiempo de ejecución total de la suite de pruebas unitarias inferior a 5 segundos.
- **Constraints**: Cumplimiento estricto e innegociable de la Constitución v1.0.0 (`.specify/memory/constitution.md`), respeto al Contrato de compatibilidad de las Sesiones 6-8 (módulos funcionales en repositorios, firmas idénticas) y umbrales de cobertura de código verificados por `pytest-cov`.
- **Scale/Scope**: Sistema backend para gestión personal de presupuestos y gastos por categorías con aislamiento estricto entre usuarios.

---

## Constitution Check

*GATE: Evaluación previa a Phase 0 y ratificación posterior a Phase 1.*

| Artículo Constitucional | Criterio Exigido | Estado | Justificación / Mecanismo de Cumplimiento |
|---|---|---|---|
| **Artículo I: Arquitectura en capas** | Flujo `routers/` → `services/` → `repositories/`. Sin lógica de negocio en routers ni persistencia en services. | ✅ PASS | Separación en paquetes independientes bajo `app/`. Routers solo manejan HTTP; services concentran las reglas; repositories concentran queries SQLAlchemy; utils funciones puras. |
| **Artículo II: SOLID aplicado** | SRP, OCP (vía Enums), DIP mediante parámetro con valor por defecto (`repo=gastos_repository`), sin mocks. | ✅ PASS | `services/gastos.py` recibe el repositorio por parámetro (`repo=gastos_repository`), permitiendo pasar `RepositorioFalso` en tests unitarios. |
| **Artículo III: Persistencia** | SQLAlchemy + Alembic, cero SQL crudo concatenado, soporte SQLite/Postgres, `usuario_id` en cada modelo y filtro. | ✅ PASS | Modelos declarativos con foreign keys hacia `usuarios.id`. Filtro `usuario_id` forzoso en todas las consultas de gastos. |
| **Artículo IV: Seguridad** | Bcrypt (`bcrypt<4.1`), JWT con `pyjwt` (HS256), `.env` nunca versionado, identidad derivada del token (`get_current_user`), error 500 genérico, validación Pydantic. | ✅ PASS | Contraseñas nunca en texto plano; `pydantic-settings` para `.env`; `get_current_user` inyecta `usuario_id` en endpoints protegidos; captura global de excepciones devolviendo 500 genérico. |
| **Artículo V: Diseño REST** | Códigos estándar (201/200/400/401/404/422), 403 reservado para recurso ajeno explícito, paginación uniforme `skip`/`limit`, schemas `Create` vs `Out`. | ✅ PASS | Contrato REST especificado con schemas independientes (`GastoCreate`, `GastoOut`, `UsuarioCreate`, `UsuarioOut`) y códigos HTTP estándar. |
| **Artículo VI: MCP** | Tools llaman a `services/`, descripciones accionables, confirmación para destructivos, respuestas de error estructuradas, transporte `streamable-http`/`stdio`. | ✅ PASS | Tools delegadas a `services/gastos.py`. Errores capturados como `{"error": "..."}`. Identidad extraída del JWT en `streamable-http`. |
| **Artículo VII: Testing y Cobertura** | Pirámide de pruebas, `RepositorioFalso` sin `unittest.mock`, DB real en integración, `dependency_overrides` en API, cobertura: 100% reglas, ≥90% services, ≥80% global. | ✅ PASS | Suite de tests estructurada con unitarios, integración y API; exclusiones declaradas explícitamente en `pyproject.toml` para módulos de arranque. |
| **Artículo VIII: Compatibilidad** | Firmas exactas de Sesiones 6-8, repositorios como módulos de funciones sueltas (no clases), retornos primitivos (`dict`), existencia de `tests/__init__.py`. | ✅ PASS | Contrato de compatibilidad documentado e inmutable. `app/repositories/gastos.py` y `usuarios.py` implementados como módulos con funciones sueltas. |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-control-gastos/
├── spec.md              # Requerimientos, escenarios y contratos de negocio
├── plan.md              # Plan de implementación maestro y trazabilidad constitucional
├── research.md          # Investigación técnica y justificación de dependencias
├── data-model.md        # Definición del modelo relacional y esquemas Pydantic
├── quickstart.md        # Guía paso a paso de validación y ejecución
├── contracts/
│   ├── rest-api.md      # Contrato de la API REST y ejemplos JSON
│   ├── mcp-tools.md     # Contrato de herramientas MCP y manejo de sesión
│   └── compatibility.md # Firmas inmutables para compatibilidad con Sesiones 6-8
└── checklists/
    └── requirements.md  # Checklist de calidad de requerimientos
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py                   # FastAPI app, lifespan, middleware de logging, montaje MCP
├── database.py               # Engine SQLAlchemy, sessionmaker, Base, get_db
├── dependencies.py           # get_current_user, get_gastos_repo
├── core/
│   ├── __init__.py
│   ├── config.py             # Settings (pydantic-settings, SECRET_KEY, DATABASE_URL)
│   └── security.py           # pyjwt encoding/decoding, passlib CryptContext
├── models/
│   ├── __init__.py
│   ├── enums.py              # CategoriaGasto Enum y constantes
│   ├── usuario.py            # Modelo SQLAlchemy Usuario(id, email, hashed_password)
│   └── gasto.py              # Modelo SQLAlchemy Gasto(id, descripcion, monto, categoria, usuario_id)
├── schemas/
│   ├── __init__.py
│   ├── usuario.py            # UsuarioCreate, UsuarioOut, Token
│   └── gasto.py              # GastoCreate, GastoOut
├── repositories/
│   ├── __init__.py
│   ├── gastos.py             # guardar, listar, total_por_categoria (funciones sueltas)
│   └── usuarios.py           # obtener_por_email, guardar (funciones sueltas)
├── services/
│   ├── __init__.py
│   └── gastos.py             # registrar_gasto, listar_gastos, LIMITE_POR_CATEGORIA, errores
├── routers/
│   ├── __init__.py
│   ├── usuarios.py           # POST /usuarios/, POST /usuarios/token
│   └── gastos.py             # POST /gastos/, GET /gastos/
├── utils/
│   └── __init__.py           # Funciones puras independientes sin dependencias cruzadas
└── mcp/
    ├── __init__.py
    ├── server.py             # Servidor MCP montado en FastAPI vía streamable-http
    ├── auth.py               # Extracción y verificación de token JWT para MCP
    └── tools/
        ├── __init__.py
        └── gastos.py         # registrar_gasto, listar_gastos (wrappers sobre services)

alembic/
├── env.py
├── script.py.mako
└── versions/
    └── 001_initial_schema.py

alembic.ini
pyproject.toml                # Dependencias, configuración de pytest y exclusiones de cobertura
.env.example                  # Plantilla de variables de entorno (sin secretos reales)
.gitignore

tests/
├── __init__.py               # Requerido por el contrato de compatibilidad
├── conftest.py               # Fixtures compartidas (db en memoria, clientes de test)
├── test_gastos.py            # Tests unitarios con RepositorioFalso (suite Sesiones 6-8)
├── test_integracion_gastos.py# Tests de integración contra SQLite en memoria
├── test_api_gastos.py        # Tests de endpoints con TestClient y dependency_overrides
└── test_mcp_gastos.py        # Tests de herramientas MCP (casos de éxito y error)
```

**Structure Decision**: Se elige la estructura modular en capas monorepo bajo `app/` estándar de la industria para microservicios FastAPI de alto rendimiento, asegurando separación radical de responsabilidades y facilitando la ejecución de la suite de pruebas sin acoplamiento.

---

## Complexity Tracking

> **Estado**: No se presentan violaciones ni excepciones a la Constitución.

| Componente | Justificación Técnica | Alternativa Más Simple Evaluada y Razón de Descarte |
|---|---|---|
| Inyección DIP por parámetro por defecto | Permite testear unitariamente sin dependencias de DB ni `unittest.mock`. | Descartado usar contenedor IoC externo (ej. `dependency-injector`) por añadir complejidad innecesaria. |
| Repositorios como funciones sueltas | Garantiza compatibilidad estricta e inmutable con los tests de las Sesiones 6-8 (Artículo VIII). | Descartado crear clases con interfaces abstractas porque rompería los imports de los tests preexistentes. |
| Fijación `bcrypt<4.1` | Evita roturas en runtime de `passlib` debido a cambios de API en versiones nuevas de bcrypt. | Descartado usar bcrypt sin fijar versión porque provoca fallos de autenticación inesperados. |

---

## Post-Design Constitution Check

Tras completar el diseño detallado en `data-model.md`, `contracts/` y `quickstart.md`, se re-evalúan los 8 Artículos Constitucionales:
- **Resultado**: 100% de cumplimiento.
- **Riesgos identificados**: Ninguno.
- **Listo para generación de tareas**: Se procede a `/speckit-tasks`.
