"""
Servicio de Usuario
Contiene la lógica de autenticación y gestión de usuarios
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session
from app.models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from app.repositories.usuario_repository import UsuarioRepository
from app.core.security import (
    hash_password,
    verify_password,
    validar_politica_contrasena,
    crear_access_token,
    registrar_intento_fallido,
    limpiar_intentos_fallidos,
    esta_bloqueado
)
from app.core.roles import RolEnum


class UsuarioService:
    """
    Servicio que orquesta la lógica de autenticación y usuarios.
    - Registro de usuarios
    - Autenticación (login)
    - Gestión de contraseñas
    - Bloqueo por seguridad
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.usuario_repo = UsuarioRepository(session)
    
    def registrar_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        """
        Crea un nuevo usuario.
        
        Args:
            usuario_data: Datos del usuario a crear
            
        Returns:
            Usuario: Usuario creado
            
        Raises:
            ValueError: Si email ya existe o contraseña no cumple políticas
        """
        # Validar email único
        existente = self.usuario_repo.get_by_email(usuario_data.email)
        if existente:
            raise ValueError(f"El email {usuario_data.email} ya está registrado")
        
        # Validar política de contraseña
        es_valida, mensaje = validar_politica_contrasena(usuario_data.contraseña)
        if not es_valida:
            raise ValueError(f"Contraseña insegura: {mensaje}")
        
        # Hash de la contraseña
        contraseña_hash = hash_password(usuario_data.contraseña)
        
        # Crear usuario
        nuevo_usuario = Usuario(
            nombre_completo=usuario_data.nombre_completo,
            email=usuario_data.email,
            contraseña_hash=contraseña_hash,
            rol=usuario_data.rol
        )
        
        usuario_creado = self.usuario_repo.create(nuevo_usuario)
        return usuario_creado
    
    def autenticar(self, email: str, contraseña: str) -> tuple[bool, Optional[Usuario], str]:
        """
        Autentica un usuario (login).
        
        Args:
            email: Email del usuario
            contraseña: Contraseña en texto plano
            
        Returns:
            tuple: (éxito, usuario, mensaje)
        """
        # Verificar si está bloqueado
        bloqueado, motivo = esta_bloqueado(email)
        if bloqueado:
            return False, None, motivo
        
        # Buscar usuario
        usuario = self.usuario_repo.get_by_email(email)
        if not usuario:
            registrar_intento_fallido(email)
            return False, None, "Email o contraseña incorrectos"
        
        # Verificar si está activo
        if not usuario.activo:
            return False, None, "Usuario desactivado"
        
        # Verificar contraseña
        if not verify_password(contraseña, usuario.contraseña_hash):
            registrar_intento_fallido(email)
            return False, None, "Email o contraseña incorrectos"
        
        # Login exitoso
        limpiar_intentos_fallidos(email)
        
        # Actualizar fecha de último acceso
        usuario.fecha_ultimo_acceso = datetime.utcnow()
        self.usuario_repo.update(usuario.id, {"fecha_ultimo_acceso": datetime.utcnow()})
        
        return True, usuario, "Login exitoso"
    
    def crear_token(self, usuario: Usuario) -> str:
        """
        Crea un JWT para un usuario autenticado.
        
        Args:
            usuario: Usuario autenticado
            
        Returns:
            str: Token JWT
        """
        token_data = {
            "sub": str(usuario.id),
            "usuario_id": usuario.id,
            "email": usuario.email,
            "rol": usuario.rol
        }
        return crear_access_token(token_data)
    
    def obtener_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID."""
        return self.usuario_repo.get_by_id(usuario_id)
    
    def obtener_todos_usuarios(self, skip: int = 0, limit: int = 20) -> List[Usuario]:
        """Obtiene todos los usuarios."""
        return self.usuario_repo.get_all(skip=skip, limit=limit)
    
    def actualizar_usuario(
        self,
        usuario_id: int,
        usuario_update: UsuarioUpdate
    ) -> Optional[Usuario]:
        """Actualiza los datos de un usuario."""
        return self.usuario_repo.update(usuario_id, usuario_update.dict(exclude_unset=True))
    
    def cambiar_contrasena(
        self,
        usuario_id: int,
        contrasena_actual: str,
        contrasena_nueva: str
    ) -> tuple[bool, str]:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            usuario_id: ID del usuario
            contrasena_actual: Contraseña actual
            contrasena_nueva: Nueva contraseña
            
        Returns:
            tuple: (éxito, mensaje)
        """
        usuario = self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado"
        
        # Verificar contraseña actual
        if not verify_password(contrasena_actual, usuario.contraseña_hash):
            return False, "Contraseña actual incorrecta"
        
        # Validar nueva contraseña
        es_valida, mensaje = validar_politica_contrasena(contrasena_nueva)
        if not es_valida:
            return False, f"Contraseña insegura: {mensaje}"
        
        # Actualizar contraseña
        nuevo_hash = hash_password(contrasena_nueva)
        self.usuario_repo.update(
            usuario_id,
            {
                "contraseña_hash": nuevo_hash,
                "fecha_cambio_contrasena": datetime.utcnow()
            }
        )
        
        return True, "Contraseña actualizada correctamente"
    
    def eliminar_usuario(self, usuario_id: int) -> bool:
        """Elimina un usuario."""
        return self.usuario_repo.delete(usuario_id)
