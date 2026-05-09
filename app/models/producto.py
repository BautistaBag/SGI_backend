"""
Modelo de Producto
Define la estructura de la tabla 'producto' en la base de datos
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class Producto(SQLModel, table=True):
    """
    Modelo que representa un producto en el inventario.
    
    Attributes:
        id: Identificador único del producto
        codigo: Código único del producto (SKU)
        nombre: Nombre del producto
        descripcion: Descripción detallada del producto
        precio: Precio unitario del producto
        stock_actual: Cantidad actual en inventario
        stock_minimo: Cantidad mínima recomendada
        categoria_id: Referencia a la categoría del producto
        activo: Indica si el producto está disponible
        fecha_creacion: Timestamp de creación
        fecha_actualizacion: Timestamp de última actualización
    """
    
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(
        index=True,
        unique=True,
        min_length=1,
        max_length=50,
        description="Código único del producto (SKU)"
    )
    nombre: str = Field(
        index=True,
        min_length=1,
        max_length=200,
        description="Nombre del producto"
    )
    descripcion: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Descripción detallada del producto"
    )
    precio: Decimal = Field(
        gt=0,
        decimal_places=2,
        max_digits=10,
        description="Precio unitario del producto"
    )
    stock_actual: int = Field(
        default=0,
        ge=0,  # CHECK CONSTRAINT: stock_actual >= 0
        description="Cantidad actual en inventario"
    )
    stock_minimo: int = Field(
        default=10,
        ge=0,
        description="Cantidad mínima recomendada"
    )
    categoria_id: int = Field(
        foreign_key="categoria.id",
        description="Referencia a la categoría del producto"
    )
    activo: bool = Field(
        default=True,
        description="Indica si el producto está disponible"
    )
    fecha_creacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del registro"
    )
    fecha_actualizacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de última actualización"
    )


class ProductoCreate(SQLModel):
    """Schema para crear un nuevo producto"""
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    stock_actual: int = 0
    stock_minimo: int = 10
    categoria_id: int
    activo: bool = True


class ProductoUpdate(SQLModel):
    """Schema para actualizar un producto"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = None
    stock_minimo: Optional[int] = None
    activo: Optional[bool] = None


class ProductoResponse(SQLModel):
    """Schema de respuesta para producto (sin timestamp interno)"""
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    stock_actual: int
    stock_minimo: int
    categoria_id: int
    activo: bool
