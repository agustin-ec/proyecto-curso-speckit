<!--
Sync Impact Report:
- Version change: Unratified template → 1.0.0
- List of modified principles:
  - [PRINCIPLE_1_NAME] → I. Arquitectura en capas
  - [PRINCIPLE_2_NAME] → II. SOLID aplicado (no teórico)
  - [PRINCIPLE_3_NAME] → III. Persistencia
  - [PRINCIPLE_4_NAME] → IV. Seguridad (no negociable)
  - [PRINCIPLE_5_NAME] → V. Diseño de endpoints REST
- Added principles / sections:
  - VI. MCP: tools y reutilización
  - VII. Testing y cobertura
  - VIII. Compatibilidad con el proyecto de referencia
- Removed sections:
  - [SECTION_2_NAME] (contenido absorbido en Artículos III, IV, V y VI)
  - [SECTION_3_NAME] (contenido absorbido en Artículos VII, VIII y Gobernanza)
- Follow-up TODOs: Ninguno. Todos los artículos y gobernanza quedaron completamente especificados.
-->

# Control de Gastos Constitution

## Core Principles

### I. Arquitectura en capas
1. `routers/` reciben la solicitud HTTP, delegan al service correspondiente y traducen su resultado (o excepción) a una respuesta HTTP. Un router NUNCA valida reglas de negocio (ej. "el monto debe ser positivo") — esa lógica vive exclusivamente en `services/`.
2. `services/` contienen toda la lógica de negocio. Un service NUNCA importa SQLAlchemy, `Session`, ni ningún detalle de persistencia directamente.
3. `repositories/` son la única capa autorizada a leer o escribir en la base de datos. Un repository no contiene reglas de negocio, solo operaciones de persistencia (guardar, listar, buscar, sumar).
4. `utils/` son funciones puras (mismo input → mismo output, sin efectos secundarios), sin importar nada de `services/`, `routers/` ni `repositories/`.
5. `mcp/tools/` NUNCA reimplementan lógica de `services/`. Si una tool de MCP y un router necesitan la misma regla, ambos llaman al mismo service.

### II. SOLID aplicado (no teórico)
1. **SRP (Single Responsibility Principle)**: Cada función de `services/` hace una sola cosa. La validación (`_validar_x`) DEBE estar separada de la orquestación (`registrar_x`).
2. **OCP (Open/Closed Principle)**: Agregar una categoría, un tipo de gasto o una regla nueva se hace agregando un valor a una constante o `Enum`, NUNCA reescribiendo un `if` ya existente.
3. **DIP (Dependency Inversion Principle)**: Todo service que necesite un repository DEBE recibirlo como parámetro con un valor por defecto (`def registrar_gasto(..., repo=gastos_repo)`), NUNCA importarlo fijo dentro del cuerpo de la función. Esto es innegociable: es lo que permite testear sin `unittest.mock`.
4. **LSP e ISP pragmáticos**: No se fuerza LSP ni ISP si el proyecto no tiene jerarquías de clases ni interfaces formales — queda prohibido agregar complejidad artificial para cumplir un principio que no aplica todavía.

### III. Persistencia
1. SQLAlchemy como ORM y Alembic para migraciones. NINGUNA sentencia SQL cruda concatenada con strings está permitida.
2. SQLite en desarrollo; el código de `database.py` DEBE funcionar contra Postgres sin tocar `services/` ni `routers/` (usar `connect_args` condicional solo para SQLite).
3. Cada modelo con datos de usuario DEBE incluir `usuario_id` como FK. NINGUNA consulta de datos de usuario puede omitir el filtro por `usuario_id`.

### IV. Seguridad (no negociable)
1. **Contraseñas**: Hash con `passlib[bcrypt]`. NUNCA se guarda ni se loguea una contraseña en texto plano.
2. **Autenticación**: OAuth2 password flow + JWT firmado con HS256. `ACCESS_TOKEN_EXPIRE_MINUTES` DEBE ser configurable, NUNCA infinito.
3. **Secretos**: `SECRET_KEY` y `DATABASE_URL` viven SOLO en `.env` (nunca versionado). `.env.example` documenta las variables necesarias sin valores reales. `SECRET_KEY` DEBE generarse con `openssl rand -hex 32` o equivalente criptográficamente seguro, NUNCA escrito a mano.
4. **Autorización estricta**: El `usuario_id` para filtrar, crear o modificar un gasto SIEMPRE sale del token JWT decodificado (`get_current_user`), NUNCA de un parámetro de la URL, del body, ni de un query param. Esto aplica también a recursos ya existentes, no solo a la creación: cualquier operación sobre un gasto por `id` (leer, actualizar, eliminar) primero DEBE verificar que ese gasto pertenece al usuario autenticado antes de manipularlo.
5. **Manejo de errores no controlados**: Una excepción no controlada (`Exception` genérica) devuelve `500` con `{"detail": "Error interno del servidor"}` — NUNCA un stack trace ni el mensaje de la excepción original al cliente. El detalle técnico sí se loguea internamente.
6. **Validación de entradas**: Toda entrada de usuario se DEBE validar con schemas Pydantic antes de llegar a `services/`.

### V. Diseño de endpoints REST
1. **Convención de verbos y códigos HTTP**:
   - `POST`: Crea (`201`).
   - `GET`: Lista o lee (`200`).
   - Fallo de autenticación: `401`.
   - Recurso no encontrado: `404`.
   - Error de validación de schema: `422`.
   - Error de regla de negocio conocido: `400` con `{"detail": "..."}`.
   - `403`: Se reserva exclusivamente para cuando el recurso solicitado existe pero pertenece a otro usuario y la operación lo identifica por `id` explícito en la ruta (ej. `PATCH /gastos/{id}`). Un listado (`GET /gastos/`) NUNCA devuelve `403`; simplemente filtra por el `usuario_id` del JWT y nunca expone ni acepta datos de otro usuario.
2. **Paginación uniforme**: Toda lista paginada DEBE exponer `skip` y `limit` como query params, con valores por defecto razonables (ej. `skip=0, limit=20`); valores inválidos (negativos, no numéricos) constituyen error de schema (`422`).
3. **Separación de schemas**: Los schemas de entrada y salida son estrictamente distintos (`GastoCreate` vs `GastoOut`) — NUNCA se expone el modelo de SQLAlchemy directamente.

### VI. MCP: tools y reutilización
1. **Reutilización obligatoria**: Cada tool de MCP llama a una función de `services/`, sin excepción. Si una tool necesita lógica que no existe en `services/`, esa lógica se agrega en `services/` primero, y la tool la reutiliza — nunca al revés.
2. **Descripciones específicas**: La descripción de cada tool DEBE ser específica y accionable (ej. "Registra un gasto con descripción, monto y categoría, validando el límite mensual por categoría"), nunca genérica ("maneja gastos").
3. **Manejo de errores de negocio**: Los errores de negocio se devuelven como una estructura clara (`{"error": "..."}`), NUNCA como una excepción sin controlar que rompa la sesión del cliente MCP.
4. **Transporte e identidad**: Si el transporte es `stdio` y no hay forma de propagar identidad real de usuario, se documenta explícitamente en el código como simplificación consciente (comentario), nunca como un olvido silencioso. Si el transporte es `streamable-http` y hay un token verificado, la tool DEBE usar la identidad de ese token (nunca un usuario demo hardcodeado) — el usuario demo es solo el fallback legítimo cuando no hay ningún token disponible.
5. **Operaciones destructivas**: Cualquier tool con efecto destructivo (ej. `eliminar_gasto`) DEBE pedir confirmación explícita gestionada por el servidor, nunca depender de que el modelo decida preguntar por su cuenta.

### VII. Testing y cobertura
1. **Pirámide de pruebas obligatoria**: Unitarias (mayoría) → Integración → API/E2E (minoría).
2. **Inyección de dependencias para tests unitarios**: Tests unitarios de `services/` inyectan un repositorio falso (que cumple el mismo contrato que el real) como parámetro — está PROHIBIDO usar `unittest.mock` para esto, aprovechando el diseño con DIP.
3. **Cobertura mínima exigida**:
   - 100% de las reglas de negocio explícitas de `spec.md` cubiertas por al menos un test unitario cada una (ej. categoría inválida, límite excedido, monto inválido) — cobertura estricta de *reglas*, no solo de líneas.
   - Cobertura de líneas de `services/` ≥ 90%.
   - Cobertura de líneas del conjunto `services/ + repositories/ + routers/ + utils/` ≥ 80%, medida con `pytest --cov=app --cov-report=term-missing`. Este umbral NO exige cubrir el arranque de la app (`main.py`: lifespan, montaje ASGI de MCP, middleware de logging), el servidor MCP en sí (`mcp/server.py`, `mcp/auth.py`) ni `logging_config.py` — son infraestructura de arranque, no lógica de negocio, y su exclusión se declara explícitamente en `[tool.coverage.run] omit` de `pyproject.toml`, nunca como una omisión silenciosa.
4. **Entorno de integración**: Tests de integración corren contra una base de datos real (SQLite en memoria como mínimo), nunca contra el repositorio falso.
5. **Aislamiento en tests de API**: Tests de API usan `app.dependency_overrides` de FastAPI para sustituir `get_db`, `get_gastos_repo` y `get_current_user` — nunca levantan un servidor real ni golpean la base de datos de desarrollo.
6. **Validación de tools MCP**: Toda tool de MCP tiene al menos dos tests: un caso exitoso y un caso de error de negocio, verificados directamente o vía MCP Inspector.
7. **Criterio de terminación (DoD)**: Ninguna tarea de `tasks.md` se considera terminada sin su test correspondiente en verde.

### VIII. Compatibilidad con el proyecto de referencia
1. **Preservación de contrato de tests**: Este proyecto reconstruye el sistema "Gastos" de las Sesiones 6-8, cuya suite de tests (`test_gastos.py`, `test_integracion_gastos.py`, `test_api_gastos.py`) se copia sin modificar sus aserciones. Los módulos, funciones, parámetros (nombre y orden) y excepciones que esos tests importan son un contrato fijo, no una sugerencia — se documentan en una sección "Contrato de compatibilidad" de `spec.md` y ninguna tarea de `tasks.md` puede renombrar, reordenar o eliminar un símbolo de esa lista.
2. **Estructura funcional de repositorios**: `repositories/gastos.py` y `repositories/usuarios.py` son módulos con funciones sueltas, no clases — el contrato de compatibilidad así lo fija. Un repository devuelve estructuras simples (`dict`, o el objeto de dominio ya existente), nunca expone el objeto de sesión de SQLAlchemy al llamador.

## Governance

1. **Supremacía constitucional**: Esta constitución tiene prioridad sobre cualquier decisión tomada durante `/speckit-implement`, arquitectura o refactorización. Si el agente o desarrollador necesita desviarse de un artículo, DEBE señalarlo explícitamente y esperar aprobación formal antes de continuar, sin excepciones ni decisiones silenciosas.
2. **Procedimiento de enmienda**: Cualquier modificación a los principios requiere documentar la justificación, presentar el Sync Impact Report, actualizar la constitución y registrar el cambio en el historial de control de versiones.
3. **Política de versionado semántico (SemVer)**:
   - **MAJOR**: Modificaciones incompatibles, eliminación o redefinición sustancial de principios.
   - **MINOR**: Incorporación de nuevos principios, artículos o expansión material de guías existentes.
   - **PATCH**: Correcciones tipográficas, aclaraciones de redacción o refinamientos no semánticos.
4. **Revisiones de cumplimiento**: Toda especificación (`spec.md`), plan (`plan.md`) y lista de tareas (`tasks.md`) debe verificarse contra estos 8 artículos antes de iniciar la implementación.

**Version**: 1.0.0 | **Ratified**: 2026-09-15 | **Last Amended**: 2026-09-15
