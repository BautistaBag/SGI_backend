"""
Dependencias de Seguridad - FastAPI
Validación de JWT, roles y permisos en los endpoints
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlmodel import Session
from app.models.usuario import TokenData, Usuario
from app.core.database import get_session
from app.core.security import verificar_token
from app.core.roles import RolEnum, tiene_permiso
from app.repositories.usuario_repository import UsuarioRepository

# Esquema de seguridad
security = HTTPBearer()


async def obtener_usuario_actual(
    credentials: HTTPAuthCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> TokenData:
    """
    Valida el JWT y extrae los datos del usuario.
    Se usa como dependencia en endpoints protegidos.
    
    Args:
        credentials: Token JWT del header Authorization
        session: Sesión de base de datos
        
    Returns:
        TokenData: Datos extraídos del token
        
    Raises:
        HTTPException: Si el token es inválido o expirado
    """
    token = credentials.credentials
    
    # Verificar token
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer datos
    usuario_id = payload.get("usuario_id")
    email = payload.get("email")
    rol = payload.get("rol")
    
    if not usuario_id or not email or not rol:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token incompleto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenData(usuario_id=usuario_id, email=email, rol=RolEnum(rol))


async def obtener_usuario_bd(
    token_data: TokenData = Depends(obtener_usuario_actual),
    session: Session = Depends(get_session)
) -> Usuario:
    """
    Obtiene el usuario completo de la base de datos.
    
    Args:
        token_data: Datos extraídos del JWT
        session: Sesión de base de datos
        
    Returns:
        Usuario: Usuario de la base de datos
        
    Raises:
        HTTPException: Si el usuario no existe o está inactivo
    """
    usuario_repo = UsuarioRepository(session)
    usuario = usuario_repo.get_by_id(token_data.usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    return usuario


def requiere_rol(*roles_permitidos: RolEnum):
    """
    Decorator que valida que el usuario tenga uno de los roles permitidos.
    
    Uso:
        @router.get("/ruta")
        def mi_endpoint(usuario = Depends(requiere_rol(RolEnum.ADMIN))):
            pass
    
    Args:
        roles_permitidos: Roles permitidos para acceder
        
    Returns:
        Función que valida el rol
    """
    async def validar_rol(
        usuario: Usuario = Depends(obtener_usuario_bd)
    ) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de estos roles: {', '.join([r.value for r in roles_permitidos])}"
            )
        return usuario
    
    return validar_rol


def requiere_permiso(permiso: str):
    """
    Decorator que valida que el usuario tenga permiso para una acción específica.
    
    Uso:
        @router.post("/productos")
        def crear_producto(usuario = Depends(requiere_permiso("crear_producto"))):
            pass
    
    Args:
        permiso: Nombre del permiso a validar
        
    Returns:
        Función que valida el permiso
    """
    async def validar_permiso(
        usuario: Usuario = Depends(obtener_usuario_bd)
    ) -> Usuario:
        if not tiene_permiso(usuario.rol, permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para: {permiso}"
            )
        return usuario
    
    return validar_permiso
