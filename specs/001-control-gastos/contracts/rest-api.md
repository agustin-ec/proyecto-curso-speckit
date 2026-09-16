# Interface Contract: REST API

**Feature**: [`specs/001-control-gastos/spec.md`](../spec.md)  
**Date**: 2026-09-15  
**Protocol**: HTTP/1.1 (JSON)  
**Base URL**: `/`

Este documento define la especificación detallada de los endpoints REST del sistema de control de gastos, en conformidad con el **Artículo V** de la Constitución del Proyecto.

---

## Resumen de Endpoints

| Método | Ruta | Autenticación | Payload Request | Respuesta Éxito | Códigos de Error |
|---|---|---|---|---|---|
| `POST` | `/usuarios/` | No | `{"email": "...", "password": "..."}` | `201 Created` | `400` (email duplicado), `422` (validación) |
| `POST` | `/usuarios/token` | No | Form Data: `username`, `password` | `200 OK` | `401` (credenciales inválidas) |
| `POST` | `/gastos/` | Sí (Bearer JWT) | `{"descripcion": "...", "monto": 10.5, "categoria": "comida"}` | `201 Created` | `400` (cat inválida / límite excedido), `401`, `422` |
| `GET` | `/gastos/` | Sí (Bearer JWT) | Query: `skip=0`, `limit=20` | `200 OK` | `401`, `422` (parámetros inválidos) |

---

## 1. Registro de Usuario: `POST /usuarios/`

Crea una nueva cuenta de usuario en el sistema.

- **Headers**:
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "PasswordSeguro123!"
  }
  ```
- **Respuestas**:
  - **`201 Created`**:
    ```json
    {
      "id": 1,
      "email": "usuario@ejemplo.com"
    }
    ```
  - **`400 Bad Request`** (Email ya registrado):
    ```json
    {
      "detail": "El email ya está registrado"
    }
    ```
  - **`422 Unprocessable Entity`** (Formato de email inválido o contraseña vacía):
    ```json
    {
      "detail": [
        {
          "loc": ["body", "email"],
          "msg": "value is not a valid email address",
          "type": "value_error"
        }
      ]
    }
    ```

---

## 2. Autenticación y Token: `POST /usuarios/token`

Genera un token JWT de acceso siguiendo el estándar OAuth2 Password Flow.

- **Headers**:
  - `Content-Type: application/x-www-form-urlencoded`
- **Request Form Body**:
  - `username`: Correo electrónico del usuario (ej. `usuario@ejemplo.com`).
  - `password`: Contraseña en texto plano.
- **Respuestas**:
  - **`200 OK`**:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```
  - **`401 Unauthorized`** (Credenciales inválidas):
    ```json
    {
      "detail": "Credenciales inválidas"
    }
    ```

---

## 3. Registro de Gasto: `POST /gastos/`

Registra un nuevo gasto para el usuario autenticado, verificando todas las reglas de negocio.

- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "descripcion": "Almuerzo de trabajo",
    "monto": 45.50,
    "categoria": "comida"
  }
  ```
- **Respuestas**:
  - **`201 Created`**:
    ```json
    {
      "id": 1,
      "descripcion": "Almuerzo de trabajo",
      "monto": 45.5,
      "categoria": "comida",
      "usuario_id": 1
    }
    ```
  - **`400 Bad Request`** (Categoría no permitida):
    ```json
    {
      "detail": "Categoría inválida: vacaciones"
    }
    ```
  - **`400 Bad Request`** (Límite de 500.0 excedido en la categoría):
    ```json
    {
      "detail": "El gasto excede el límite de 500.0 para la categoría comida"
    }
    ```
  - **`401 Unauthorized`** (Sin token o token inválido):
    ```json
    {
      "detail": "No autenticado"
    }
    ```
  - **`422 Unprocessable Entity`** (`monto <= 0` o `descripcion` vacía):
    ```json
    {
      "detail": [
        {
          "loc": ["body", "monto"],
          "msg": "Input should be greater than 0",
          "type": "greater_than"
        }
      ]
    }
    ```

---

## 4. Listado Paginado de Gastos: `GET /gastos/`

Retorna la lista de gastos pertenecientes **únicamente** al usuario autenticado.

- **Headers**:
  - `Authorization: Bearer <access_token>`
- **Query Parameters**:
  - `skip` (*opcional, int, default: 0*): Cantidad de registros a omitir (debe ser `>= 0`).
  - `limit` (*opcional, int, default: 20*): Cantidad máxima de registros a retornar (debe ser `> 0`).
- **Respuestas**:
  - **`200 OK`**:
    ```json
    [
      {
        "id": 1,
        "descripcion": "Almuerzo de trabajo",
        "monto": 45.5,
        "categoria": "comida",
        "usuario_id": 1
      },
      {
        "id": 2,
        "descripcion": "Boleto de metro",
        "monto": 2.5,
        "categoria": "transporte",
        "usuario_id": 1
      }
    ]
    ```
  - **`401 Unauthorized`** (Sin token o token inválido):
    ```json
    {
      "detail": "No autenticado"
    }
    ```
  - **`422 Unprocessable Entity`** (Parámetros `skip` o `limit` inválidos):
    ```json
    {
      "detail": [
        {
          "loc": ["query", "skip"],
          "msg": "Input should be greater than or equal to 0",
          "type": "greater_than_equal"
        }
      ]
    }
    ```
