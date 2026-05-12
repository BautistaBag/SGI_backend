"""
Servicio de Movimiento
Contiene la lógica de negocio para movimientos de inventario
Aquí se ejecutan las transacciones atómicas críticas
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session
from app.models.movimiento import Movimiento, MovimientoCreate
from app.models.producto import Producto
from app.repositories.movimiento_repository import MovimientoRepository
from app.repositories.producto_repository import ProductoRepository
from app.core.config import settings


class MovimientoService:
    """
    Servicio que orquesta movimientos de inventario.
    - Validación de reglas de negocio
    - Transacciones atómicas (stock y movimiento juntos)
    - Prevención de stock negativo
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.movimiento_repo = MovimientoRepository(session)
        self.producto_repo = ProductoRepository(session)
    
    def registrar_salida(
        self, 
        producto_id: int, 
        cantidad: int, 
        motivo: Optional[str] = None,
        usuario_id: Optional[int] = None
    ) -> Movimiento:
        """
        Registra una salida de inventario (venta, descuento, etc).
        Validación crítica: el stock no puede quedar negativo.
        
        TRANSACCIÓN ATÓMICA: Si falla algo, todo se revierte.
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a restar
            motivo: Motivo de la salida
            usuario_id: ID del usuario que registra
            
        Returns:
            Movimiento: Movimiento registrado
            
        Raises:
            ValueError: Si stock insuficiente
        """
        # 1. Validar tipo de movimiento permitido
        if "SALIDA" not in settings.TIPOS_MOVIMIENTO_VALIDOS:
            raise ValueError("SALIDA no es un tipo de movimiento válido")
        
        # 2. Obtener producto con lock para lectura
        producto = self.producto_repo.get_by_id(producto_id)
        if not producto:
            raise ValueError(f"Producto {producto_id} no existe")
        
        if not producto.activo:
            raise ValueError(f"Producto {producto_id} está inactivo")
        
        # 3. VALIDACIÓN CRÍTICA: Verificar si hay stock suficiente
        if producto.stock_actual - cantidad < settings.STOCK_MINIMO_PERMITIDO:
            raise ValueError(
                f"Stock insuficiente. Disponible: {producto.stock_actual}, "
                f"Solicitado: {cantidad}"
            )
        
        # 4. Actualizar stock (dentro de la transacción)
        producto_actualizado = self.producto_repo.restar_stock(producto_id, cantidad)
        
        # 5. Crear registro de movimiento
        movimiento = Movimiento(
            tipo="SALIDA",
            producto_id=producto_id,
            cantidad=-cantidad,  # Negativo para salidas
            motivo=motivo,
            usuario_id=usuario_id,
            precio_unitario=producto.precio
        )
        
        movimiento_registrado = self.movimiento_repo.create(movimiento)
        
        # 6. Commit de la transacción atómica
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Error al registrar movimiento: {str(e)}")
        
        return movimiento_registrado
    
    def registrar_entrada(
        self, 
        producto_id: int, 
        cantidad: int, 
        motivo: Optional[str] = None,
        usuario_id: Optional[int] = None
    ) -> Movimiento:
        """
        Registra una entrada de inventario (compra, devolución, etc).
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a sumar
            motivo: Motivo de la entrada
            usuario_id: ID del usuario que registra
            
        Returns:
            Movimiento: Movimiento registrado
            
        Raises:
            ValueError: Si producto no existe
        """
        # Validar producto
        producto = self.producto_repo.get_by_id(producto_id)
        if not producto:
            raise ValueError(f"Producto {producto_id} no existe")
        
        # Actualizar stock
        producto_actualizado = self.producto_repo.sumar_stock(producto_id, cantidad)
        
        # Crear movimiento
        movimiento = Movimiento(
            tipo="ENTRADA",
            producto_id=producto_id,
            cantidad=cantidad,
            motivo=motivo,
            usuario_id=usuario_id,
            precio_unitario=producto.precio
        )
        
        movimiento_registrado = self.movimiento_repo.create(movimiento)
        
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Error al registrar movimiento: {str(e)}")
        
        return movimiento_registrado
    
    def obtener_movimientos_producto(
        self, 
        producto_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Movimiento]:
        """Obtiene historial de movimientos de un producto."""
        return self.movimiento_repo.get_by_producto(producto_id, skip=skip, limit=limit)
    
    def obtener_movimientos_por_fecha(
        self, 
        fecha_inicio: datetime, 
        fecha_fin: datetime,
        skip: int = 0, 
        limit: int = 20
    ) -> List[Movimiento]:
        """Obtiene movimientos dentro de un rango de fechas."""
        return self.movimiento_repo.get_by_fecha_rango(
            fecha_inicio, fecha_fin, skip=skip, limit=limit
        )
    
    def registrar_movimiento(
        self,
        tipo: str,
        producto_id: int,
        cantidad: int,
        motivo: Optional[str] = None,
        usuario_id: Optional[int] = None
    ) -> Movimiento:
        """
        Registra un movimiento genérico (ENTRADA o SALIDA).
        Usa el tipo para decidir qué operación hacer.
        
        Args:
            tipo: "ENTRADA" o "SALIDA"
            producto_id: ID del producto
            cantidad: Cantidad a mover
            motivo: Motivo del movimiento
            usuario_id: ID del usuario
            
        Returns:
            Movimiento: Movimiento registrado
            
        Raises:
            ValueError: Si tipo no es válido o hay validación fallida
        """
        tipo = tipo.upper()
        
        if tipo == "ENTRADA":
            return self.registrar_entrada(producto_id, cantidad, motivo, usuario_id)
        elif tipo == "SALIDA":
            return self.registrar_salida(producto_id, cantidad, motivo, usuario_id)
        else:
            raise ValueError(f"Tipo de movimiento no válido: {tipo}. Use ENTRADA o SALIDA")
