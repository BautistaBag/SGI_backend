"""
Repositorio de Movimiento
Contiene consultas específicas para la tabla 'movimiento'
"""
from typing import List
from datetime import datetime
from sqlmodel import Session, select
from app.models.movimiento import Movimiento
from app.repositories.base_repository import BaseRepository


class MovimientoRepository(BaseRepository[Movimiento]):
    """
    Repositorio específico para operaciones con movimientos.
    """
    
    def __init__(self, session: Session):
        super().__init__(session, Movimiento)
    
    def get_by_producto(self, producto_id: int, skip: int = 0, limit: int = 100) -> List[Movimiento]:
        """
        Obtiene todos los movimientos de un producto.
        
        Args:
            producto_id: ID del producto
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Movimiento]: Lista de movimientos del producto
        """
        statement = (
            select(Movimiento)
            .where(Movimiento.producto_id == producto_id)
            .order_by(Movimiento.fecha_movimiento.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_by_tipo(self, tipo: str, skip: int = 0, limit: int = 100) -> List[Movimiento]:
        """
        Obtiene todos los movimientos de un tipo específico.
        
        Args:
            tipo: Tipo de movimiento (ENTRADA, SALIDA, etc.)
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Movimiento]: Lista de movimientos del tipo especificado
        """
        statement = (
            select(Movimiento)
            .where(Movimiento.tipo == tipo)
            .order_by(Movimiento.fecha_movimiento.desc())
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
    ) -> List[Movimiento]:
        """
        Obtiene movimientos dentro de un rango de fechas.
        
        Args:
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Movimiento]: Lista de movimientos en el rango
        """
        statement = (
            select(Movimiento)
            .where(Movimiento.fecha_movimiento >= fecha_inicio)
            .where(Movimiento.fecha_movimiento <= fecha_fin)
            .order_by(Movimiento.fecha_movimiento.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
