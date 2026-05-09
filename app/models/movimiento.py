"""
Modelo de Movimiento de Inventario
Define la estructura de la tabla 'movimiento' para registrar todas las transacciones
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class Movimiento(SQLModel, table=True):
    """
    Modelo que registra cada movimiento de inventario.
    Permite auditoría y trazabilidad completa de cambios de stock.
    
    Attributes:
        id: Identificador único del movimiento
        tipo: Tipo de movimiento (ENTRADA, SALIDA, AJUSTE, TRANSFERENCIA)
        producto_id: Referencia al producto afectado
        cantidad: Cantidad movida (positiva o negativa)
        motivo: Motivo del movimiento (opcional pero recomendado)
        usuario_id: Usuario que registró el movimiento (para auditoría)
        precio_unitario: Precio del producto en el momento del movimiento
        fecha_movimiento: Fecha en que ocurrió el movimiento
        fecha_registro: Fecha en que se registró en el sistema
    """
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str = Field(
        index=True,
        description="Tipo de movimiento: ENTRADA, SALIDA, AJUSTE, TRANSFERENCIA"
    )
    producto_id: int = Field(
        foreign_key="producto.id",
        index=True,
        description="Referencia al producto afectado"
    )
    cantidad: int = Field(
        description="Cantidad movida (puede ser negativa para salidas)"
    )
    motivo: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Motivo del movimiento"
    )
    usuario_id: Optional[int] = Field(
        default=None,
        description="ID del usuario que registró el movimiento (para auditoría)"
    )
    precio_unitario: Decimal = Field(
        default=0,
        decimal_places=2,
        max_digits=10,
        description="Precio unitario en el momento del movimiento"
    )
    fecha_movimiento: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Fecha en que ocurrió el movimiento"
    )
    fecha_registro: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de registro en el sistema"
    )


class MovimientoCreate(SQLModel):
    """Schema para crear un nuevo movimiento"""
    tipo: str
    producto_id: int
    cantidad: int
    motivo: Optional[str] = None
    usuario_id: Optional[int] = None


class MovimientoResponse(SQLModel):
    """Schema de respuesta para movimiento"""
    id: int
    tipo: str
    producto_id: int
    cantidad: int
    motivo: Optional[str] = None
    usuario_id: Optional[int] = None
    precio_unitario: Decimal
    fecha_movimiento: datetime
