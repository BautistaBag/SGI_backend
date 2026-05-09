"""
Modelo de Usuario
Define la estructura de la tabla 'usuario' con roles y autenticación
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from app.core.roles import RolEnum


class Usuario(SQLModel, table=True):
    """
    Modelo que representa un usuario del sistema.
    
    Attributes:
        id: Identificador único del usuario
        nombre_completo: Nombre completo del usuario
        email: Email único del usuario
        contraseña_hash: Contraseña hasheada con bcrypt
        rol: Rol del usuario (ADMIN, OPERADOR, LECTURA)
        activo: Indica si el usuario puede acceder al sistema
        intentos_fallidos: Contador de intentos de login fallidos
        bloqueado_hasta: Timestamp hasta cuando está bloqueado (por seguridad)
        fecha_creacion: Fecha de creación de la cuenta
        fecha_ultimo_acceso: Última vez que accedió
        fecha_cambio_contrasena: Última vez que cambió la contraseña
    """
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_completo: str = Field(
        min_length=1,
        max_length=200,
        description="Nombre completo del usuario"
    )
    email: str = Field(
        index=True,
        unique=True,
        description="Email único del usuario"
    )
    contraseña_hash: str = Field(
        description="Contraseña hasheada (nunca guardar en texto plano)"
    )
    rol: RolEnum = Field(
        default=RolEnum.LECTURA,
        description="Rol del usuario: ADMIN, OPERADOR, LECTURA"
    )
    activo: bool = Field(
        default=True,
        description="Indica si el usuario puede acceder al sistema"
    )
    intentos_fallidos: int = Field(
        default=0,
        description="Contador de intentos de login fallidos"
    )
    bloqueado_hasta: Optional[datetime] = Field(
        default=None,
        description="Timestamp hasta cuando está bloqueado por seguridad"
    )
    fecha_creacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación de la cuenta"
    )
    fecha_ultimo_acceso: Optional[datetime] = Field(
        default=None,
        description="Última vez que accedió al sistema"
    )
    fecha_cambio_contrasena: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última vez que cambió la contraseña"
    )


class UsuarioCreate(SQLModel):
    """Schema para crear un nuevo usuario"""
    nombre_completo: str
    email: str
    contraseña: str
    rol: RolEnum = RolEnum.LECTURA


class UsuarioUpdate(SQLModel):
    """Schema para actualizar un usuario"""
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[RolEnum] = None
    activo: Optional[bool] = None


class UsuarioResponse(SQLModel):
    """Schema de respuesta para usuario (sin contraseña)"""
    id: int
    nombre_completo: str
    email: str
    rol: RolEnum
    activo: bool
    fecha_creacion: datetime
    fecha_ultimo_acceso: Optional[datetime]


class LoginRequest(SQLModel):
    """Schema para login"""
    email: str
    contraseña: str


class LoginResponse(SQLModel):
    """Schema de respuesta para login"""
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class TokenData(SQLModel):
    """Datos extraídos del JWT"""
    usuario_id: int
    email: str
    rol: RolEnum
