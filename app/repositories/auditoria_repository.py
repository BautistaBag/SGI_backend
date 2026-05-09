"""
Repositorio de Auditoría
Contiene consultas específicas para la tabla 'auditoria'
"""
from typing import List
from datetime import datetime
from sqlmodel import Session, select
from app.models.auditoria import Auditoria
from app.repositories.base_repository import BaseRepository


class AuditoriaRepository(BaseRepository[Auditoria]):
    """
    Repositorio específico para operaciones con auditoría.
    Nota: Solo permite INSERT, no UPDATE/DELETE.
    """
    
    def __init__(self, session: Session):
        super().__init__(session, Auditoria)
    
    def get_by_entidad(
        self, 
        entidad: str, 
        entidad_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Auditoria]:
        """
        Obtiene el historial de cambios de una entidad específica.
        
        Args:
            entidad: Tipo de entidad (PRODUCTO, CATEGORIA, etc.)
            entidad_id: ID de la entidad
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Auditoria]: Lista de cambios ordenados por fecha
        """
        statement = (
            select(Auditoria)
            .where(Auditoria.entidad == entidad)
            .where(Auditoria.entidad_id == entidad_id)
            .order_by(Auditoria.fecha_cambio.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_by_fecha_rango(
        self, 
        fecha_inicio: datetime, 
        fecha_fin: datetime, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Auditoria]:
        """
        Obtiene cambios dentro de un rango de fechas.
        
        Args:
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Auditoria]: Lista de cambios en el rango
        """
        statement = (
            select(Auditoria)
            .where(Auditoria.fecha_cambio >= fecha_inicio)
            .where(Auditoria.fecha_cambio <= fecha_fin)
            .order_by(Auditoria.fecha_cambio.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_by_usuario(
        self, 
        usuario_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Auditoria]:
        """
        Obtiene todos los cambios realizados por un usuario.
        
        Args:
            usuario_id: ID del usuario
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Auditoria]: Lista de cambios del usuario
        """
        statement = (
            select(Auditoria)
            .where(Auditoria.usuario_id == usuario_id)
            .order_by(Auditoria.fecha_cambio.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
