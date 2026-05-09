"""
Repositorio de Usuario
Contiene consultas específicas para la tabla 'usuario'
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.models.usuario import Usuario
from app.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    """
    Repositorio específico para operaciones con usuarios.
    """
    
    def __init__(self, session: Session):
        super().__init__(session, Usuario)
    
    def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        statement = select(Usuario).where(Usuario.email == email)
        return self.session.exec(statement).first()
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtiene solo usuarios activos.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Usuario]: Lista de usuarios activos
        """
        statement = (
            select(Usuario)
            .where(Usuario.activo == True)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_by_rol(self, rol: str, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtiene usuarios por rol.
        
        Args:
            rol: Rol a filtrar
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Usuario]: Lista de usuarios con ese rol
        """
        statement = (
            select(Usuario)
            .where(Usuario.rol == rol)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
