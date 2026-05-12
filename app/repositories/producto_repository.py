"""
Repositorio de Producto
Contiene consultas específicas para la tabla 'producto'
"""
from typing import Optional, List
from sqlmodel import Session, select, join
from app.models.producto import Producto
from app.models.categoria import Categoria
from app.repositories.base_repository import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    """
    Repositorio específico para operaciones con productos.
    Hereda operaciones CRUD básicas de BaseRepository.
    """
    
    def __init__(self, session: Session):
        super().__init__(session, Producto)
    
    def get_by_codigo(self, codigo: str) -> Optional[Producto]:
        """
        Obtiene un producto por su código único (SKU).
        
        Args:
            codigo: Código del producto
            
        Returns:
            Producto: Producto encontrado o None
        """
        statement = select(Producto).where(Producto.codigo == codigo)
        return self.session.exec(statement).first()
    
    def get_by_categoria(self, categoria_id: int, skip: int = 0, limit: int = 100) -> List[Producto]:
        """
        Obtiene todos los productos de una categoría.
        
        Args:
            categoria_id: ID de la categoría
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Producto]: Lista de productos en esa categoría
        """
        statement = (
            select(Producto)
            .where(Producto.categoria_id == categoria_id)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[Producto]:
        """
        Obtiene solo los productos activos.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Producto]: Lista de productos activos
        """
        statement = (
            select(Producto)
            .where(Producto.activo == True)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_stock_bajo(self, skip: int = 0, limit: int = 100) -> List[Producto]:
        """
        Obtiene productos cuyo stock está por debajo del mínimo.
        Útil para alertas.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Producto]: Lista de productos con stock bajo
        """
        statement = (
            select(Producto)
            .where(Producto.stock_actual <= Producto.stock_minimo)
            .where(Producto.activo == True)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def restar_stock(self, producto_id: int, cantidad: int) -> Optional[Producto]:
        """
        Resta stock de un producto (operación atómica).
        Se usa con transacciones en la capa de servicio.
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a restar
            
        Returns:
            Producto: Producto actualizado o None
            
        Raises:
            ValueError: Si quedaría stock negativo
        """
        producto = self.get_by_id(producto_id)
        if not producto:
            return None
        
        if producto.stock_actual - cantidad < 0:
            raise ValueError(f"Stock insuficiente. Disponible: {producto.stock_actual}")
        
        producto.stock_actual -= cantidad
        self.session.add(producto)
        self.session.flush()  # Asegurar que la actualización se persista en la BD
        return producto
    
    def sumar_stock(self, producto_id: int, cantidad: int) -> Optional[Producto]:
        """
        Suma stock a un producto (operación atómica).
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a sumar
            
        Returns:
            Producto: Producto actualizado o None
        """
        producto = self.get_by_id(producto_id)
        if not producto:
            return None
        
        producto.stock_actual += cantidad
        self.session.add(producto)
        return producto
    
    def get_with_categoria(
        self, 
        categoria_nombre: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[tuple]:
        """
        Obtiene productos con información de categoría, opcionalmente filtrado por nombre de categoría.
        
        Retorna una lista de tuplas (Producto, Categoria) para permitir acceso a ambas entidades
        con la información de categoría incluida.
        
        Args:
            categoria_nombre: Nombre de la categoría para filtrar (case-insensitive, opcional)
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[tuple]: Lista de tuplas (Producto, Categoria)
        """
        statement = select(Producto, Categoria).join(
            Categoria, Producto.categoria_id == Categoria.id
        ).where(Producto.activo == True)
        
        # Si se proporciona nombre de categoría, filtrar por él (case-insensitive)
        if categoria_nombre:
            statement = statement.where(
                Categoria.nombre.ilike(f"%{categoria_nombre}%")
            )
        
        statement = statement.offset(skip).limit(limit)
        return self.session.exec(statement).all()
