# Feature Specification: Sistema de Control de Gastos Personales

**Feature Directory**: `specs/001-control-gastos`

**Feature Branch**: `001-control-gastos`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Sistema de control de gastos personales. Entidades: Usuario, Gasto. Reglas de negocio: categorías válidas (comida, transporte, entretenimiento, otros), monto > 0, descripción no vacía, límite acumulado de 500 por categoría, aislamiento estricto por usuario autenticado. Contrato REST, MCP, contrato de compatibilidad con tests de referencia de Sesiones 6-8."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro y Autenticación de Usuario (Priority: P1)

Como nuevo usuario del sistema, deseo registrarme con mi dirección de correo electrónico y contraseña, e iniciar sesión para recibir un token de acceso, de modo que pueda operar el sistema de manera segura y confidencial.

**Why this priority**: Sin un mecanismo de identidad y autenticación, resulta inviable asociar gastos de forma segura y aislar los datos privados de cada usuario.

**Independent Test**: Puede probarse de forma totalmente autónoma registrando una nueva cuenta de usuario, validando la unicidad del correo electrónico y solicitando exitosamente un token de acceso JWT.

**Acceptance Scenarios**:

1. **Given** un email no registrado y una contraseña válida, **When** el usuario solicita la creación de su cuenta en `/usuarios/`, **Then** el sistema crea la cuenta con código `201`, retorna los datos del usuario y jamás expone la contraseña ni su hash.
2. **Given** un email que ya existe en el sistema, **When** se intenta registrar nuevamente en `/usuarios/`, **Then** el sistema responde con error `400` indicando correo electrónico duplicado.
3. **Given** un usuario registrado con credenciales correctas, **When** envía sus credenciales al endpoint de token `/usuarios/token`, **Then** el sistema responde con código `200` y entrega un token JWT firmado.
4. **Given** credenciales inválidas (email o contraseña incorrectos), **When** se solicita un token en `/usuarios/token`, **Then** el sistema rechaza la solicitud con código `401 Unauthorized`.

---

### User Story 2 - Registro de Gastos con Reglas de Negocio (Priority: P1)

Como usuario autenticado, deseo registrar gastos individuales ingresando descripción, monto y categoría, asegurando que se validen las reglas de negocio (monto positivo, descripción no vacía, categoría permitida y límite de 500 por categoría).

**Why this priority**: Constituye la funcionalidad de valor nuclear del sistema financiero personal.

**Independent Test**: Puede verificarse registrando gastos válidos y comprobando el guardado y respuesta `201`, así como enviando gastos inválidos o que excedan el límite acumulado para constatar el rechazo con código `400`.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con un total acumulado en la categoría "comida" de 300, **When** registra un gasto con monto 150, categoría "comida" y descripción "Almuerzo", **Then** el sistema registra el gasto, retorna código `201` y el gasto queda asociado al usuario.
2. **Given** un usuario autenticado, **When** intenta registrar un gasto con una categoría no reconocida (distinta de `comida`, `transporte`, `entretenimiento`, `otros`), **Then** el sistema rechaza la operación con código `400` y error de categoría inválida (`CategoriaInvalidaError`).
3. **Given** un usuario autenticado, **When** intenta registrar un gasto con monto menor o igual a cero o con descripción vacía, **Then** el sistema rechaza la petición con error de validación `422`.
4. **Given** un usuario autenticado con un total acumulado de 450 en "transporte", **When** intenta registrar un gasto de 60 en "transporte", **Then** el sistema rechaza la operación con código `400` y error de límite excedido (`LimiteExcedidoError`), sin persistir el gasto ya que el acumulado resultante (510) supera 500.
5. **Given** un usuario autenticado con un total acumulado de 350 en "comida", **When** registra un gasto de exactamente 150 en "comida" (llevando el acumulado a exactamente 500.00), **Then** la operación ESTÁ PERMITIDA, se acepta con código `201` y se persiste exitosamente (no cuenta como excedido).

---

### User Story 3 - Consulta y Listado de Gastos Propios Paginados (Priority: P2)

Como usuario autenticado, deseo consultar la lista de mis gastos con soporte de paginación para auditar mi historial financiero de forma ordenada, asegurando que jamás se muestren gastos de otros usuarios.

**Why this priority**: Brinda visibilidad y control sobre los gastos registrados previamente, manteniendo aislamiento total entre usuarios.

**Independent Test**: Puede probarse creando registros con dos cuentas de usuario independientes y validando que cada cuenta solo obtenga sus propios registros al consultar `GET /gastos/`.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con múltiples gastos registrados, **When** consulta `GET /gastos/?skip=0&limit=20`, **Then** el sistema retorna la lista de sus gastos con código `200` respetando los parámetros de paginación.
2. **Given** un usuario autenticado y una solicitud a `GET /gastos/` que intenta enviar identificadores de otros usuarios por parámetros externos, **When** se procesa la solicitud, **Then** el sistema ignora cualquier identificador externo, filtra estrictamente por el `usuario_id` del token JWT y retorna únicamente los gastos propios.
3. **Given** un cliente que envía parámetros de paginación inválidos (ej. `skip < 0` o `limit` no numérico), **When** solicita el listado, **Then** el sistema responde con código `422`.

---

### User Story 4 - Gestión de Gastos mediante Protocolo MCP (Priority: P2)

Como agente o asistente de IA integrado mediante Model Context Protocol (MCP), deseo invocar las herramientas `registrar_gasto` y `listar_gastos` para gestionar las finanzas del usuario con la misma lógica de negocio y restricciones que la API REST.

**Why this priority**: Facilita la automatización agéntica y la paridad funcional entre la API web y los asistentes IA.

**Independent Test**: Invocar las herramientas MCP bajo transporte HTTP/stdio comprobando la resolución de identidad, respuesta exitosa estructurada y captura de errores de negocio.

**Acceptance Scenarios**:

1. **Given** una sesión MCP autenticada, **When** se invoca `registrar_gasto(descripcion, monto, categoria)` con datos válidos, **Then** se retorna el diccionario estructurado del gasto creado.
2. **Given** una invocación a `registrar_gasto` con una categoría inválida o superando el límite acumulado, **When** se ejecuta la herramienta, **Then** se retorna una estructura controlada `{"error": "<mensaje>"}` sin romper la sesión MCP.
3. **Given** una invocación a `listar_gastos(skip, limit)`, **When** se ejecuta la herramienta, **Then** retorna la lista de gastos del usuario autenticado en la sesión MCP.

---

### Edge Cases

- **Monto límite exacto**: Un gasto que cause que el acumulado en una categoría llegue a exactamente 500.00 DEBE ser aceptado; solo se rechaza si el acumulado resultante es estrictamente mayor a 500.00.
- **Monto en cero o negativo**: Cualquier valor `<= 0` en el campo monto DEBE ser rechazado inmediatamente.
- **Descripción en blanco**: Cadenas compuestas exclusivamente por espacios en blanco o vacías DEBEN ser rechazadas como inválidas.
- **Solicitud sin token**: Cualquier llamada a endpoints o tools que requieran autenticación sin token o con token expirado/inválido DEBE responder inmediatamente con `401 Unauthorized`.
- **Fuga de identidad externa**: Envíos maliciosos de `usuario_id` en query params, body o headers de petición son estrictamente ignorados; la identidad proviene únicamente del token de sesión decodificado.
- **Transporte MCP stdio vs HTTP**: En transporte `streamable-http`, la identidad proviene del token verificado. En `stdio` sin propagación de token, se admite el usuario demo configurado en entorno como fallback explícitamente documentado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir el registro de usuarios con correo electrónico único y contraseña obligatoria.
- **FR-002**: El sistema DEBE almacenar las contraseñas hasheadas de forma segura (usando bcrypt) y NUNCA devolver la contraseña ni su hash en ninguna respuesta.
- **FR-003**: El sistema DEBE ofrecer un endpoint de autenticación mediante flujo OAuth2 Password que emita tokens JWT con tiempo de expiración configurable.
- **FR-004**: El sistema DEBE validar que toda solicitud a rutas protegidas (`/gastos/`) contenga un token JWT válido, respondiendo con `401` en caso contrario.
- **FR-005**: El sistema DEBE permitir registrar gastos con `descripcion` no vacía, `monto` numérico mayor a cero y `categoria` válida.
- **FR-006**: El sistema DEBE restringir las categorías permitidas estrictamente al conjunto: `comida`, `transporte`, `entretenimiento`, `otros`. Cualquier otro valor DEBE generar un error de negocio (`CategoriaInvalidaError` / `400`).
- **FR-007**: El sistema DEBE calcular el monto total acumulado por categoría para el usuario y rechazar (`LimiteExcedidoError` / `400`) cualquier gasto que haga que el total acumulado en dicha categoría sea mayor a `500.0`.
- **FR-008**: El sistema DEBE garantizar el aislamiento total de datos: un usuario solo puede crear y visualizar sus propios gastos, derivando el `usuario_id` exclusivamente del token JWT decodificado.
- **FR-009**: El sistema DEBE soportar listado paginado de gastos mediante los parámetros `skip` (por defecto 0) y `limit` (por defecto 20).
- **FR-010**: El sistema DEBE exponer herramientas MCP (`registrar_gasto`, `listar_gastos`) que deleguen su ejecución a los mismos servicios de dominio, retornando errores estructurados `{"error": "..."}` ante fallos de negocio.

### Key Entities

- **Usuario**: Representa la cuenta de un individuo registrado.
  - Atributos: `id` (entero único / PK), `email` (cadena única no vacía), `hashed_password` (cadena de hash criptográfico).
  - Relaciones: Posee cero o más gastos asociados.
- **Gasto**: Representa una erogación económica individual.
  - Atributos: `id` (entero único / PK), `descripcion` (cadena no vacía), `monto` (flotante/decimal estrictamente > 0), `categoria` (cadena perteneciente al Enum de categorías), `usuario_id` (clave foránea hacia Usuario).
  - Relaciones: Pertenece a exactamente un Usuario.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de registro de gastos con categorías no autorizadas son rechazados con el error de negocio correspondiente.
- **SC-002**: El 100% de los gastos que excederían el límite acumulado de 500 por categoría son prevenidos y rechazados antes de ser persistidos.
- **SC-003**: 0% de fuga de información entre cuentas de usuario: ninguna consulta o mutación puede acceder a datos de otro usuario.
- **SC-004**: El 100% de las peticiones sin autenticación válida a endpoints protegidos reciben código de estado `401`.
- **SC-005**: 100% de consistencia entre la API REST y las tools MCP: ambas interfaces producen idénticos resultados y respetan las mismas validaciones de negocio.

## Contrato de la API (REST)

| Método | Ruta | Auth | Request (Body / Query) | Éxito | Errores esperados |
|---|---|---|---|---|---|
| `POST` | `/usuarios/` | No | Body JSON: `email`, `password` | `201` Schema `UsuarioOut` | `400` email duplicado, `422` validación |
| `POST` | `/usuarios/token` | No | Form data: `username`, `password` | `200` `{"access_token": "...", "token_type": "bearer"}` | `401` credenciales inválidas |
| `POST` | `/gastos/` | Sí (Bearer) | Body JSON: `descripcion`, `monto`, `categoria` | `201` Schema `GastoOut` | `400` categoría inválida, `400` límite excedido, `401`, `422` |
| `GET` | `/gastos/` | Sí (Bearer) | Query: `skip` (int, default 0), `limit` (int, default 20) | `200` Lista de `GastoOut` | `401`, `422` (skip/limit inválidos) |

## Contrato equivalente por MCP

- **Tool `registrar_gasto(descripcion, monto, categoria)`**:
  - Mismo comportamiento y reglas que `POST /gastos/`.
  - Retorna diccionario del gasto creado o diccionario con error de negocio estructurado: `{"error": "..."}`.
  - Opera sobre el usuario autenticado de la sesión MCP.
- **Tool `listar_gastos(skip=0, limit=20)`**:
  - Mismo comportamiento y paginación que `GET /gastos/`.
  - Retorna la lista de diccionarios de gastos del usuario autenticado.
- **Resolución de Identidad**:
  - Transporte `streamable-http`: Identidad resuelta desde el token JWT verificado.
  - Transporte `stdio`: Fallback documentado a usuario demo de `.env` únicamente cuando no hay canal para propagar token.

## Contrato de compatibilidad (no negociable)

La suite de tests heredada de las Sesiones 6-8 (`test_gastos.py`, `test_integracion_gastos.py`, `test_api_gastos.py`) se copiará sin alterar sus aserciones ni importaciones. Fija de manera inalterable las siguientes firmas y símbolos:

- **`app/services/gastos.py`**:
  - Excepciones: `CategoriaInvalidaError`, `LimiteExcedidoError`.
  - Constante: `LIMITE_POR_CATEGORIA = 500.0`.
  - Función: `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict` (orden posicional exacto, `repo` como keyword argument con default).
  - Función: `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]`.
- **`app/repositories/gastos.py`** (módulo con funciones sueltas, NO clase):
  - `guardar(db, usuario_id, descripcion, monto, categoria) -> dict`.
  - `listar(db, usuario_id, skip=0, limit=20) -> list[dict]`.
  - `total_por_categoria(db, usuario_id, categoria) -> float`.
  - Retornan siempre `dict` o estructuras primitivas, jamás objetos SQLAlchemy directos.
- **`app/repositories/usuarios.py`**:
  - `obtener_por_email(db, email) -> Usuario | None`.
  - `guardar(db, email, hashed_password) -> Usuario`.
- **Símbolos y dependencias de compatibilidad**:
  - `app.database.get_db`
  - `app.dependencies.get_current_user`
  - `app.dependencies.get_gastos_repo`
  - `app.models.usuario.Usuario(id=, email=, hashed_password=)`
- **Soporte de test suite**:
  - `tests/__init__.py` DEBE existir para permitir la importación `from tests.test_gastos import RepositorioFalso` en `test_api_gastos.py`.

## Casos de error explícitos para pruebas

1. Registrar gasto con monto negativo o cero (`<= 0`).
2. Registrar gasto con categoría inexistente o no autorizada.
3. Registrar gasto que ocasione que el total acumulado en su categoría supere el límite de `500.0`.
4. Listar o registrar gastos sin token de autenticación (`401 Unauthorized`).
5. Listar gastos enviando identificador de otro usuario manualmente (debe ignorarse completamente, nunca filtrar por ese ID).

## Assumptions

- El límite de 500 por categoría aplica sobre la suma de gastos acumulados del usuario en el alcance actual del sistema.
- Las categorías válidas están definidas en un Enum / tupla cerrada: `{"comida", "transporte", "entretenimiento", "otros"}`.
- La base de datos es SQLite para desarrollo y pruebas, compatible con PostgreSQL sin alterar capas superiores.
- Los montos numéricos operan con precisión de punto flotante/decimal estándar.
