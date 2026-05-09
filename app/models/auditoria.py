"""
Modelo de Auditoría
Define la tabla para registrar cambios históricos en los datos críticos
(precios, nombres, stock anterior, etc.)
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Auditoria(SQLModel, table=True):
    """
    Modelo que registra cambios en atributos críticos de los productos.
    Proporciona historial completo para cumplimiento normativo.
    
    Attributes:
        id: Identificador único del registro de auditoría
        entidad: Tipo de entidad auditada (PRODUCTO, CATEGORIA, etc.)
        entidad_id: ID de la entidad afectada
        campo_modificado: Campo que fue modificado
        valor_anterior: Valor antes del cambio
        valor_nuevo: Valor después del cambio
        usuario_id: ID del usuario que realizó el cambio
        motivo: Motivo del cambio (opcional)
        fecha_cambio: Timestamp del cambio
    """
    
    id: Optional[int] = Field(default=None, primary_key=True)
    entidad: str = Field(
        index=True,
        description="Tipo de entidad: PRODUCTO, CATEGORIA, etc."
    )
    entidad_id: int = Field(
        index=True,
        description="ID de la entidad auditada"
    )
    campo_modificado: str = Field(
        description="Nombre del campo modificado (ej: precio, nombre, stock)"
    )
    valor_anterior: str = Field(
        description="Valor antes del cambio (convertido a string para flexibilidad)"
    )
    valor_nuevo: str = Field(
        description="Valor después del cambio"
    )
    usuario_id: Optional[int] = Field(
        default=None,
        description="ID del usuario que realizó el cambio"
    )
    motivo: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Motivo del cambio"
    )
    fecha_cambio: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Timestamp del cambio"
    )
    
    class Config:
        """Configuración para proteger integridad de auditoría"""
        # Solo INSERT permitido, no UPDATE/DELETE
        frozen = True


class AuditoriaCreate(SQLModel):
    """Schema para crear un registro de auditoría"""
    entidad: str
    entidad_id: int
    campo_modificado: str
    valor_anterior: str
    valor_nuevo: str
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None


class AuditoriaResponse(SQLModel):
    """Schema de respuesta para auditoría"""
    id: int
    entidad: str
    entidad_id: int
    campo_modificado: str
    valor_anterior: str
    valor_nuevo: str
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None
    fecha_cambio: datetime
