"""
Rutas de Autenticación
Endpoints para login, registro y gestión de contraseñas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.models.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    LoginRequest,
    LoginResponse,
    Usuario
)
from app.services.usuario_service import UsuarioService
from app.api.seguridad import obtener_usuario_bd

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioResponse)
def registro(
    usuario_data: UsuarioCreate,
    session: Session = Depends(get_session)
):
    """
    Registra un nuevo usuario en el sistema.
    
    Validaciones:
    - Email debe ser único
    - Contraseña debe cumplir política de seguridad
    """
    try:
        servicio = UsuarioService(session)
        usuario = servicio.registrar_usuario(usuario_data)
        return usuario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login(
    credenciales: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Autentica un usuario y retorna un JWT.
    
    - Valida email y contraseña
    - Bloquea cuenta tras 5 intentos fallidos
    - Retorna token JWT válido por 30 minutos
    """
    servicio = UsuarioService(session)
    
    # Autenticar usuario
    exito, usuario, mensaje = servicio.autenticar(
        credenciales.email,
        credenciales.contraseña
    )
    
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=mensaje
        )
    
    # Crear token
    token = servicio.crear_token(usuario)
    
    return LoginResponse(
        access_token=token,
        usuario=usuario
    )


@router.post("/cambiar-contrasena")
def cambiar_contrasena(
    contraseña_actual: str,
    contraseña_nueva: str,
    usuario: Usuario = Depends(obtener_usuario_bd),
    session: Session = Depends(get_session)
):
    """
    Cambia la contraseña del usuario autenticado.
    
    Requiere:
    - Token JWT válido
    - Contraseña actual correcta
    - Nueva contraseña debe cumplir política
    """
    servicio = UsuarioService(session)
    
    exito, mensaje = servicio.cambiar_contrasena(
        usuario.id,
        contraseña_actual,
        contraseña_nueva
    )
    
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    
    return {"mensaje": mensaje}


@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil(
    usuario: Usuario = Depends(obtener_usuario_bd)
):
    """
    Obtiene los datos del usuario autenticado.
    
    Requiere: Token JWT válido
    """
    return usuario
