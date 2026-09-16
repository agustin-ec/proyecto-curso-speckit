# Quickstart & Validation Guide: Control de Gastos

**Feature**: [`specs/001-control-gastos/spec.md`](spec.md)  
**Date**: 2026-09-15  
**Artifacts Relacionados**:
- [Modelo de Datos](data-model.md)
- [Contrato REST API](contracts/rest-api.md)
- [Contrato MCP Tools](contracts/mcp-tools.md)
- [Contrato de Compatibilidad](contracts/compatibility.md)

Este documento es una guía práctica paso a paso para configurar el entorno local, ejecutar la suite completa de pruebas unitarias, de integración y de API, y validar manualmente el comportamiento del sistema a través de la API REST y el servidor MCP.

---

## 1. Prerrequisitos

- **Python**: Versión 3.11 o superior.
- **Gestor de paquetes**: `pip` y entorno virtual `venv` (o `poetry`).
- **Herramientas de línea de comando**: `curl` y `sqlite3`.

---

## 2. Configuración del Entorno Local

1. **Crear y activar el entorno virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias del proyecto**:
   ```bash
   pip install fastapi "uvicorn[standard]" "sqlalchemy>=2.0" alembic pyjwt \
       "passlib[bcrypt]" "bcrypt<4.1" pydantic-settings email-validator \
       python-multipart "mcp" pytest pytest-cov httpx
   ```

3. **Configurar variables de entorno**:
   Crear el archivo `.env` en la raíz del proyecto (basado en `.env.example`):
   ```bash
   SECRET_KEY=e83a9f72b6c1482098bdfc7891045a2e37920194bc0285a974b216cd08e75e92
   DATABASE_URL=sqlite:///./gastos.db
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   DEMO_USER_EMAIL=demo@gastos.local
   ```

4. **Inicializar la base de datos y migraciones**:
   ```bash
   alembic upgrade head
   ```

---

## 3. Ejecución de Pruebas y Reporte de Cobertura

Conforme al **Artículo VII** de la Constitución, para validar la integridad del sistema y verificar los umbrales mínimos de cobertura exigidos:

```bash
# Ejecutar toda la suite de pruebas con reporte de cobertura
pytest --cov=app --cov-report=term-missing
```

### Umbrales exigidos (Artículo VII.3):
- **100% de reglas de negocio** cubiertas por tests unitarios.
- **≥ 90% de líneas** en `app/services/`.
- **≥ 80% de líneas** en el conjunto `app/services/ + app/repositories/ + app/routers/ + app/utils/`.

---

## 4. Validación Manual Paso a Paso (API REST)

1. **Iniciar el servidor de desarrollo**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Crear un nuevo usuario**:
   ```bash
   curl -X POST http://localhost:8000/usuarios/ \
     -H "Content-Type: application/json" \
     -d '{"email": "test@ejemplo.com", "password": "PasswordSeguro123"}'
   # Esperado: 201 Created con {"id": 1, "email": "test@ejemplo.com"}
   ```

3. **Obtener el token JWT**:
   ```bash
   TOKEN=$(curl -s -X POST http://localhost:8000/usuarios/token \
     -d "username=test@ejemplo.com&password=PasswordSeguro123" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
   echo "Token: $TOKEN"
   # Esperado: Token JWT alfanumérico
   ```

4. **Registrar un gasto válido (acumulado: 200.0)**:
   ```bash
   curl -X POST http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Supermercado", "monto": 200.0, "categoria": "comida"}'
   # Esperado: 201 Created
   ```

5. **Registrar un gasto en el límite exacto (acumulado previo 200 + 300 = 500.0)**:
   ```bash
   curl -X POST http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Cena familiar", "monto": 300.0, "categoria": "comida"}'
   # Esperado: 201 Created (llegar exactamente a 500.0 ESTÁ PERMITIDO)
   ```

6. **Intentar registrar un gasto que exceda el límite acumulado (500.0 + 0.50 = 500.50)**:
   ```bash
   curl -X POST http://localhost:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Café", "monto": 0.50, "categoria": "comida"}'
   # Esperado: 400 Bad Request con {"detail": "El gasto excede el límite de 500.0 para la categoría comida"}
   ```

7. **Consultar la lista paginada de gastos propios**:
   ```bash
   curl -X GET "http://localhost:8000/gastos/?skip=0&limit=10" \
     -H "Authorization: Bearer $TOKEN"
   # Esperado: 200 OK con los 2 gastos creados
   ```

---

## 5. Validación de Tools MCP

El servidor MCP se monta sobre el endpoint `/mcp` de la misma aplicación FastAPI.

1. **Inspección de herramientas**:
   Utilizar MCP Inspector o cliente MCP configurando el transporte SSE / streamable-http hacia `http://localhost:8000/mcp` pasando el header `Authorization: Bearer <TOKEN>`.
2. **Invocación de `registrar_gasto`**:
   - Parámetros: `{"descripcion": "Taxi", "monto": 15.0, "categoria": "transporte"}`.
   - Resultado esperado: Objeto JSON con el registro creado.
3. **Invocación de `listar_gastos`**:
   - Parámetros: `{"skip": 0, "limit": 20}`.
   - Resultado esperado: Array JSON con los gastos del usuario autenticado.
