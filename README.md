# Sistema de Gestión de Inventario (SGI) - Backend

## 📋 Descripción General

Backend del Sistema de Gestión de Inventario construido con **FastAPI** y **SQLModel**, implementando arquitectura por capas con separación clara de responsabilidades: rutas, servicios, repositorios y modelos.

El sistema gestiona:
- **Productos** con categorías y stock
- **Movimientos de inventario** (entradas, salidas, ajustes)
- **Auditoría de cambios** (historial de modificaciones)
- **Autenticación y autorización** con JWT y control de roles

---

## 🔒 Seguridad: Roles, Perfiles y Contraseñas

### Sistema de Roles y Permisos

El sistema implementa **Control de Acceso Basado en Roles (RBAC)** con tres niveles:

#### Roles Disponibles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **ADMIN** | Acceso total | CRUD completo de productos, categorías, movimientos, usuarios |
| **OPERADOR** | Gestión de inventario | Puede registrar entradas/salidas, ver productos (sin crear/editar) |
| **LECTURA** | Solo consulta | Solo puede ver productos y movimientos (sin modificar) |

#### Ubicación de Permisos

- **Definición de Roles:** `app/core/roles.py` - Enum con roles y matriz de permisos
- **Base de Datos:** Campo `rol` en tabla `usuario` vinculado a cada usuario
- **Validación en Backend:** Dependencias de FastAPI que validan permisos antes de ejecutar endpoints

### Manejo de Contraseñas

#### Política de Seguridad

Las contraseñas deben cumplir:
- ✅ **Longitud mínima:** 8 caracteres
- ✅ **Mayúsculas:** Al menos una letra mayúscula (A-Z)
- ✅ **Minúsculas:** Al menos una letra minúscula (a-z)
- ✅ **Números:** Al menos un dígito (0-9)
- ✅ **Caracteres especiales:** Al menos uno: `!@#$%^&*()_+-=[]{}|;:,.<>?`

#### Protección contra Ataques

- **Hashing:** Bcrypt con salt único por usuario
- **Bloqueo temporal:** La cuenta se bloquea por 15 minutos tras 5 intentos fallidos
- **Nunca almacenar:** Las contraseñas se hashean antes de guardar

**Implementación:**
```python
# app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### Protección de Endpoints con JWT

#### Flujo de Autenticación

```
1. Usuario envía email/contraseña → POST /api/auth/login
2. Backend valida credenciales
3. Servidor crea JWT con ID, Email y Rol
4. Cliente recibe token y lo guarda
5. Cliente envía token en header: Authorization: Bearer <token>
6. Middleware valida token y extrae rol
7. Si rol no tiene permiso → 403 Forbidden
8. Si rol tiene permiso → Ejecuta endpoint
```

#### Ejemplo de Uso en Endpoints

```python
# Proteger endpoint: solo ADMIN
@router.post("/productos")
def crear_producto(
    datos: ProductoCreate,
    usuario: Usuario = Depends(requiere_rol(RolEnum.ADMIN))
):
    pass

# Proteger por permiso específico
@router.post("/movimientos/salida")
def registrar_salida(
    usuario: Usuario = Depends(requiere_permiso("registrar_salida"))
):
    pass

# Solo usuarios autenticados
@router.get("/me")
def obtener_perfil(
    usuario: Usuario = Depends(obtener_usuario_bd)
):
    return usuario
```

#### Dependencias de Seguridad

- `obtener_usuario_actual()` - Valida JWT del header
- `obtener_usuario_bd()` - Trae usuario completo de BD
- `requiere_rol(*roles)` - Valida que usuario tenga uno de los roles
- `requiere_permiso(permiso)` - Valida permiso específico

---

```
┌─────────────────────────────────────────────────────────────┐
│  API (Controllers/Routes) - /app/api/routes.py              │
│  🧑‍💼 Recibe solicitudes HTTP                                │
└─────────────────────────────────────────────────────────────┘
                        ↓ Delega a
┌─────────────────────────────────────────────────────────────┐
│  Services - /app/services/*.py                              │
│  🍳 Lógica de negocio y transacciones                       │
└─────────────────────────────────────────────────────────────┘
                        ↓ Usa
┌─────────────────────────────────────────────────────────────┐
│  Repositories - /app/repositories/*.py                      │
│  📦 Acceso a datos (queries SQL)                            │
└─────────────────────────────────────────────────────────────┘
                        ↓ Consulta
┌─────────────────────────────────────────────────────────────┐
│  Database - PostgreSQL                                      │
│  💾 Almacenamiento persistente                              │
└─────────────────────────────────────────────────────────────┘
```

### Responsabilidades por Capa

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| **API** | `routes.py` | Recibir requests HTTP, validar entrada, retornar respuestas |
| **Services** | `*_service.py` | Validar reglas de negocio, ejecutar transacciones, auditoría |
| **Repositories** | `*_repository.py` | Consultas a BD, operaciones CRUD |
| **Models** | `*.py` en `/models` | Esquemas de datos y validación con Pydantic |
| **Core** | `config.py`, `database.py` | Configuración global y conexión a BD |

---

## 📁 Estructura de Carpetas

```
SGI_backend/
├── app/                           # Código principal
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # Todos los endpoints HTTP
│   ├── services/
│   │   ├── __init__.py
│   │   ├── producto_service.py    # Lógica de productos
│   │   ├── movimiento_service.py  # Lógica de movimientos
│   │   └── categoria_service.py   # Lógica de categorías
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py     # Operaciones CRUD genéricas
│   │   ├── producto_repository.py # Queries de productos
│   │   ├── movimiento_repository.py
│   │   ├── categoria_repository.py
│   │   └── auditoria_repository.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── categoria.py           # Tabla Categoría
│   │   ├── producto.py            # Tabla Producto
│   │   ├── movimiento.py          # Tabla Movimiento
│   │   └── auditoria.py           # Tabla Auditoría
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Variables de configuración
│   │   └── database.py            # Conexión a PostgreSQL
│   └── main.py                    # Punto de entrada FastAPI
├── .env                           # Variables de entorno (no commitar)
├── .gitignore                     # Archivos a ignorar en Git
├── requirements.txt               # Dependencias Python
└── README.md                      # Este archivo
```

---

## 🚀 Instalación y Setup

### Requisitos Previos
- **Python 3.11+**
- **PostgreSQL 14+**
- **pip** o **conda** como gestor de paquetes

### 1. Clonar y Entrar al Directorio
```bash
cd SGI_backend
```

### 2. Crear Entorno Virtual
```bash
# Con venv
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env  # (Si existe)

# O crear .env manualmente con tus datos
# DATABASE_URL=postgresql://user:password@localhost:5432/sgi_db
```

### 5. Crear Base de Datos en PostgreSQL
```sql
CREATE DATABASE sgi_db ENCODING 'UTF8';
```

### 6. Ejecutar la Aplicación
```bash
python -m uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000`

---

## 📚 Documentación de API

Una vez corriendo, accede a:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Ejemplos de Endpoints

#### 1. Registro de Nuevo Usuario
```bash
POST /api/auth/registro
Content-Type: application/json

{
  "nombre_completo": "Juan Pérez",
  "email": "juan@example.com",
  "contraseña": "MiContra123!@",
  "rol": "OPERADOR"
}
```

#### 2. Login - Obtener JWT
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "juan@example.com",
  "contraseña": "MiContra123!@"
}

# Respuesta:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "nombre_completo": "Juan Pérez",
    "email": "juan@example.com",
    "rol": "OPERADOR",
    "activo": true
  }
}
```

#### 3. Usar Token en Endpoints Protegidos
```bash
GET /api/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Retorna el perfil del usuario autenticado
```

#### 4. Cambiar Contraseña
```bash
POST /api/auth/cambiar-contrasena
Authorization: Bearer <token>
Content-Type: application/json

{
  "contraseña_actual": "MiContra123!@",
  "contraseña_nueva": "NuevaContra456!@"
}
```

#### 5. Crear Producto (Requiere rol ADMIN)
```bash
POST /api/productos
Authorization: Bearer <token>
Content-Type: application/json

{
  "codigo": "PROD001",
  "nombre": "Laptop",
  "descripcion": "Laptop de 15 pulgadas",
  "precio": 1200.50,
  "stock_actual": 5,
  "stock_minimo": 2,
  "categoria_id": 1,
  "activo": true
}

# Si usuario no es ADMIN: 403 Forbidden
```

#### 6. Registrar Salida (Requiere rol OPERADOR o ADMIN)
```bash
POST /api/movimientos/salida?producto_id=1&cantidad=2&motivo=Venta&usuario_id=1
Authorization: Bearer <token>

# Si usuario es LECTURA: 403 Forbidden
```

#### 7. Obtener Productos con Stock Bajo (Todos pueden)
```bash
GET /api/productos/stock/bajo
Authorization: Bearer <token>
```

---

## 🔒 Reglas de Negocio Implementadas

### 1. Stock No Negativo ✅
- **Validación en BD:** `CHECK (stock >= 0)`
- **Validación en Service:** Verifica antes de registrar salida
- **Transacciones atómicas:** Stock y movimiento se actualizan juntos

### 2. Auditoría de Cambios ✅
- Tabla aparte `auditoria` registra cambios de precio/nombre
- Solo INSERT permitido (inmutable)
- Rastrea usuario y fecha de cambio

### 3. Integridad de Datos ✅
- Relaciones FK entre tablas
- Restricciones CHECK en la BD
- Validación de datos con Pydantic

### 4. Paginación ✅
- Todos los listados soportan `skip` y `limit`
- Máximo 100 registros por página
- Mejora rendimiento con grandes datasets

---

## 🛠️ Decisiones Técnicas

### PostgreSQL
- ✅ Relaciones estrictas (FK, CHECK constraints)
- ✅ Robusto y escalable
- ✅ Soporte para transacciones ACID

### SQLModel + SQLAlchemy
- ✅ ORM robusto con seguridad SQL Injection
- ✅ Migraciones con Alembic
- ✅ Sincronización automática de esquema

### FastAPI
- ✅ Validación automática con Pydantic
- ✅ Documentación interactiva (Swagger)
- ✅ Alto rendimiento (async-ready)

### Arquitectura por Capas
- ✅ Separación de responsabilidades
- ✅ Fácil de mantener y escalar
- ✅ Testeable
- ✅ Independencia de la BD

---

## 📊 Modelos de Datos

### Tabla: `categoria`
```python
id (PK)
nombre (unique)
descripcion
activa (boolean)
fecha_creacion
fecha_actualizacion
```

### Tabla: `producto`
```python
id (PK)
codigo (unique, SKU)
nombre
descripcion
precio (> 0)
stock_actual (>= 0, CHECK CONSTRAINT)
stock_minimo
categoria_id (FK)
activo (boolean)
fecha_creacion
fecha_actualizacion
```

### Tabla: `movimiento`
```python
id (PK)
tipo (ENTRADA, SALIDA, AJUSTE, TRANSFERENCIA)
producto_id (FK)
cantidad
motivo
usuario_id (para auditoría)
precio_unitario
fecha_movimiento
fecha_registro
```

### Tabla: `auditoria`
```python
id (PK)
entidad (PRODUCTO, CATEGORIA)
entidad_id
campo_modificado
valor_anterior
valor_nuevo
usuario_id
motivo
fecha_cambio (immutable)
```

---

## 🧪 Testing (Futura Implementación)

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app
```

---

## 🐳 Deployment con Docker

```dockerfile
# Dockerfile (crear en raíz del proyecto)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build
docker build -t sgi-backend .

# Run
docker run -p 8000:8000 --env-file .env sgi-backend
```

---

## 📈 Performance y Escalabilidad

### Índices en BD
- `codigo` en `producto` (búsquedas rápidas)
- `categoria_id` en `producto`
- `tipo`, `producto_id`, `fecha_movimiento` en `movimiento`

### Paginación
- Límite máximo: 100 registros por página
- Previene timeout de queries

### Transacciones
- Operaciones críticas (movimientos) ejecutadas de forma atómica
- Rollback automático en caso de error

---

## 🚨 Seguridad

- ✅ Validación de entrada con Pydantic
- ✅ Protección SQL Injection (SQLModel ORM)
- ✅ CORS configurado
- ✅ Variables sensibles en `.env`
- ✅ Timestamps de auditoría

---

## 📝 Próximos Pasos

1. **Autenticación:** Implementar JWT para usuarios
2. **Autorización:** Roles y permisos (admin, usuario, etc.)
3. **Migraciones:** Usar Alembic para versionado de BD
4. **Logging:** Centralizar logs con ELK Stack o similar
5. **Tests:** Cobertura de tests unitarios e integración
6. **Frontend:** Conectar con React/Vue.js

---

## 👥 Contacto

Para preguntas o sugerencias sobre la arquitectura, contacta al equipo de desarrollo.

---

**Última actualización:** Mayo 2026
