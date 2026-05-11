"""
Modelo de Categoría
Define la estructura de la tabla 'categoria' en la base de datos
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Categoria(SQLModel, table=True):
    """
    Modelo que representa una categoría de productos.
    
    Attributes:
        id: Identificador único de la categoría
        nombre: Nombre de la categoría (ej: Electrónica, Ropa, etc.)
        descripcion: Descripción opcional de la categoría
        activa: Indica si la categoría está activa o desactivada
        fecha_creacion: Timestamp de creación del registro
        fecha_actualizacion: Timestamp de última actualización
    """
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(
        index=True,
        min_length=1,
        max_length=100,
        description="Nombre único de la categoría"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripción opcional de la categoría"
    )
    activa: bool = Field(
        default=True,
        description="Indica si la categoría está activa"
    )
    fecha_creacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del registro"
    )
    fecha_actualizacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de última actualización"
    )


class CategoriaCreate(SQLModel):
    """Schema para crear una nueva categoría"""
    nombre: str
    descripcion: Optional[str] = None
    activa: bool = True


class CategoriaUpdate(SQLModel):
    """Schema para actualizar una categoría"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None


class CategoriaResponse(SQLModel):
    """Schema de respuesta para categoría"""
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activa: bool
