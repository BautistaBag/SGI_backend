"""
Models - Definición de tablas y esquemas de datos
Aquí se representan las tablas de la base de datos en código Python usando SQLModel
"""
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.movimiento import Movimiento
from app.models.auditoria import Auditoria
from app.models.usuario import Usuario

__all__ = ["Categoria", "Producto", "Movimiento", "Auditoria", "Usuario"]
