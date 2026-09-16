# Interface Contract: Model Context Protocol (MCP)

**Feature**: [`specs/001-control-gastos/spec.md`](../spec.md)  
**Date**: 2026-09-15  
**Transportes**: `streamable-http` (montado en FastAPI) y `stdio`  
**Protocolo**: Model Context Protocol (MCP)

Este documento define las tools expuestas por el servidor MCP del sistema de control de gastos, en estricto cumplimiento con el **Artículo VI** de la Constitución del Proyecto.

---

## Principios de Integración MCP (Artículo VI)

1. **Reutilización directa de servicios**: Las tools MCP NO reimplementan lógica de negocio; invocan las mismas funciones de `app/services/gastos.py` que utilizan los routers de FastAPI.
2. **Descripciones accionables**: Las descripciones indican con precisión qué hace la herramienta, qué parámetros espera y qué límites valida.
3. **Manejo estructurado de errores**: Los errores de negocio (`CategoriaInvalidaError`, `LimiteExcedidoError`, errores de validación) se capturan y devuelven como diccionario estructurado:
   ```json
   {
     "error": "Mensaje detallado del error de negocio"
   }
   ```
   Bajo ninguna circunstancia se propaga una excepción no controlada que rompa el canal del cliente MCP.
4. **Resolución de Identidad**:
   - En transporte `streamable-http`: Se extrae el JWT del header `Authorization: Bearer <token>` del handshake o request HTTP.
   - En transporte `stdio`: Si no es posible inyectar tokens, se recurre de forma explícitamente documentada al usuario demo definido en `.env` (`DEMO_USER_EMAIL` / `DEMO_USER_ID`).

---

## 1. Tool: `registrar_gasto`

Registra un nuevo gasto asociado al usuario de la sesión MCP.

- **Nombre**: `registrar_gasto`
- **Descripción**: *"Registra un nuevo gasto personal con descripción, monto (>0) y categoría ('comida', 'transporte', 'entretenimiento', 'otros'), validando que el total acumulado de la categoría no supere el límite de 500.0."*
- **Parámetros (Input Schema)**:
  ```json
  {
    "type": "object",
    "properties": {
      "descripcion": {
        "type": "string",
        "description": "Descripción del gasto realizado (no puede estar vacía)"
      },
      "monto": {
        "type": "number",
        "description": "Monto económico del gasto (debe ser estrictamente mayor a 0)"
      },
      "categoria": {
        "type": "string",
        "enum": ["comida", "transporte", "entretenimiento", "otros"],
        "description": "Categoría a la que pertenece el gasto"
      }
    },
    "required": ["descripcion", "monto", "categoria"]
  }
  ```
- **Retorno Exitoso (Output Schema)**:
  ```json
  {
    "id": 1,
    "descripcion": "Cena con amigos",
    "monto": 80.0,
    "categoria": "comida",
    "usuario_id": 1
  }
  ```
- **Retornos de Error de Negocio**:
  ```json
  {
    "error": "Categoría inválida: salud"
  }
  ```
  ```json
  {
    "error": "El gasto excede el límite de 500.0 para la categoría comida"
  }
  ```

---

## 2. Tool: `listar_gastos`

Lista los gastos registrados para el usuario autenticado de la sesión MCP con soporte de paginación.

- **Nombre**: `listar_gastos`
- **Descripción**: *"Obtiene la lista paginada de gastos personales registrados por el usuario autenticado actual."*
- **Parámetros (Input Schema)**:
  ```json
  {
    "type": "object",
    "properties": {
      "skip": {
        "type": "integer",
        "default": 0,
        "description": "Número de registros a omitir para paginación (>= 0)"
      },
      "limit": {
        "type": "integer",
        "default": 20,
        "description": "Número máximo de registros a retornar (> 0)"
      }
    }
  }
  ```
- **Retorno Exitoso**:
  ```json
  [
    {
      "id": 1,
      "descripcion": "Cena con amigos",
      "monto": 80.0,
      "categoria": "comida",
      "usuario_id": 1
    }
  ]
  ```
- **Retornos de Error**:
  ```json
  {
    "error": "Parámetros de paginación inválidos"
  }
  ```
