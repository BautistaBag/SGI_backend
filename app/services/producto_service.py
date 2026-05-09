"""
Servicio de Producto
Contiene la lógica de negocio para operaciones con productos
"""
from typing import Optional, List
from sqlmodel import Session
from app.models.producto import Producto, ProductoCreate, ProductoUpdate
from app.models.auditoria import Auditoria, AuditoriaCreate
from app.repositories.producto_repository import ProductoRepository
from app.repositories.auditoria_repository import AuditoriaRepository
from app.core.config import settings


class ProductoService:
    """
    Servicio que orquesta la lógica de negocio para productos.
    - Valida reglas de negocio
    - Ejecuta transacciones
    - Registra auditoría
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.producto_repo = ProductoRepository(session)
        self.auditoria_repo = AuditoriaRepository(session)
    
    def crear_producto(self, producto_data: ProductoCreate) -> Producto:
        """
        Crea un nuevo producto con validaciones.
        
        Args:
            producto_data: Datos del producto a crear
            
        Returns:
            Producto: Producto creado
            
        Raises:
            ValueError: Si el código ya existe o hay validación fallida
        """
        # Validación: código único
        existente = self.producto_repo.get_by_codigo(producto_data.codigo)
        if existente:
            raise ValueError(f"Producto con código {producto_data.codigo} ya existe")
        
        # Validación: precio mayor a cero
        if producto_data.precio <= 0:
            raise ValueError("El precio debe ser mayor a cero")
        
        # Validación: stock no negativo (ya está en el modelo con Field(ge=0))
        if producto_data.stock_actual < 0:
            raise ValueError("El stock no puede ser negativo")
        
        # Crear producto
        nuevo_producto = Producto(**producto_data.dict())
        producto_creado = self.producto_repo.create(nuevo_producto)
        
        return producto_creado
    
    def actualizar_producto(
        self, 
        producto_id: int, 
        producto_update: ProductoUpdate,
        usuario_id: Optional[int] = None
    ) -> Optional[Producto]:
        """
        Actualiza un producto y registra los cambios en auditoría.
        
        Args:
            producto_id: ID del producto
            producto_update: Datos a actualizar
            usuario_id: ID del usuario que realiza el cambio (para auditoría)
            
        Returns:
            Producto: Producto actualizado o None
            
        Raises:
            ValueError: Si hay validación fallida
        """
        producto = self.producto_repo.get_by_id(producto_id)
        if not producto:
            return None
        
        # Preparar datos para actualizar (solo campos no None)
        update_data = producto_update.dict(exclude_unset=True)
        
        # Validaciones antes de actualizar
        if "precio" in update_data and update_data["precio"] <= 0:
            raise ValueError("El precio debe ser mayor a cero")
        
        # Registrar auditoría para cambios
        for campo, nuevo_valor in update_data.items():
            valor_anterior = str(getattr(producto, campo))
            
            # Registrar en auditoría
            auditoria = Auditoria(
                entidad="PRODUCTO",
                entidad_id=producto_id,
                campo_modificado=campo,
                valor_anterior=valor_anterior,
                valor_nuevo=str(nuevo_valor),
                usuario_id=usuario_id,
                motivo=None
            )
            self.auditoria_repo.create(auditoria)
        
        # Actualizar producto
        producto_actualizado = self.producto_repo.update(producto_id, update_data)
        
        # Commit de la transacción
        self.session.commit()
        return producto_actualizado
    
    def obtener_producto(self, producto_id: int) -> Optional[Producto]:
        """Obtiene un producto por ID."""
        return self.producto_repo.get_by_id(producto_id)
    
    def obtener_todos_productos(self, skip: int = 0, limit: int = 20) -> List[Producto]:
        """Obtiene todos los productos con paginación."""
        return self.producto_repo.get_all(skip=skip, limit=limit)
    
    def obtener_productos_stock_bajo(self, skip: int = 0, limit: int = 20) -> List[Producto]:
        """Obtiene productos con stock bajo."""
        return self.producto_repo.get_stock_bajo(skip=skip, limit=limit)
    
    def obtener_productos_activos(self, skip: int = 0, limit: int = 20) -> List[Producto]:
        """Obtiene solo productos activos."""
        return self.producto_repo.get_activos(skip=skip, limit=limit)
    
    def obtener_por_categoria(self, categoria_id: int, skip: int = 0, limit: int = 20) -> List[Producto]:
        """Obtiene productos de una categoría."""
        return self.producto_repo.get_by_categoria(categoria_id, skip=skip, limit=limit)
    
    def eliminar_producto(self, producto_id: int) -> bool:
        """
        Elimina un producto (o lo marca como inactivo).
        En sistemas reales, es mejor marcar como inactivo que eliminar.
        """
        return self.producto_repo.delete(producto_id)
