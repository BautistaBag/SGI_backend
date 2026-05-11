"""
Rutas de API
Define todos los endpoints HTTP de la aplicación
Estructura: GET, POST, PUT, DELETE para cada recurso
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.core.database import get_session
from app.models.producto import Producto, ProductoCreate, ProductoUpdate, ProductoResponse
from app.models.categoria import Categoria, CategoriaCreate, CategoriaUpdate
from app.models.movimiento import Movimiento, MovimientoResponse
from app.services.producto_service import ProductoService
from app.services.categoria_service import CategoriaService
from app.services.movimiento_service import MovimientoService

router = APIRouter(prefix="/api", tags=["API"])


# ============================================================================
# PRODUCTOS - Endpoints CRUD
# ============================================================================

@router.post("/productos", response_model=ProductoResponse, tags=["Productos"])
def crear_producto(
    producto_data: ProductoCreate,
    session: Session = Depends(get_session)
):
    """
    Crea un nuevo producto.
    
    - El código debe ser único
    - El precio debe ser mayor a 0
    - El stock no puede ser negativo
    """
    try:
        servicio = ProductoService(session)
        producto = servicio.crear_producto(producto_data)
        return producto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
def obtener_producto(
    producto_id: int,
    session: Session = Depends(get_session)
):
    """Obtiene un producto específico por ID."""
    servicio = ProductoService(session)
    producto = servicio.obtener_producto(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/productos", response_model=list[dict], tags=["Productos"])
def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    categoria: Optional[str] = Query(None, description="Filtrar por nombre de categoría (búsqueda parcial, case-insensitive)"),
    session: Session = Depends(get_session)
):
    """
    Lista todos los productos con información de categoría y paginación.
    
    **Parámetros:**
    - skip: número de registros a saltar (default: 0)
    - limit: número máximo de registros (default: 20, máx: 100)
    - categoria: filtrar por nombre de categoría (opcional, búsqueda parcial case-insensitive)
    
    **Respuesta:**
    Retorna una lista de productos con estructura:
    ```json
    {
        "id": 1,
        "codigo": "PROD001",
        "nombre": "Producto 1",
        "descripcion": "Descripción del producto",
        "precio": 99.99,
        "stock_actual": 50,
        "stock_minimo": 10,
        "activo": true,
        "categoria": {
            "id": 1,
            "nombre": "Electronica",
            "descripcion": "Categoría de electrónica",
            "activa": true
        }
    }
    ```
    
    **Ejemplos:**
    - `/api/productos` - Todos los productos con su categoría
    - `/api/productos?categoria=electronica` - Solo productos de electrónica
    - `/api/productos?skip=20&limit=10` - Paginación
    """
    servicio = ProductoService(session)
    return servicio.obtener_productos_con_categoria(
        categoria_nombre=categoria,
        skip=skip,
        limit=limit
    )


@router.get("/productos/stock/bajo", response_model=list[ProductoResponse], tags=["Productos"])
def productos_stock_bajo(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Obtiene productos con stock por debajo del mínimo."""
    servicio = ProductoService(session)
    return servicio.obtener_productos_stock_bajo(skip=skip, limit=limit)


@router.put("/productos/{producto_id}", response_model=ProductoResponse, tags=["Productos"])
def actualizar_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    session: Session = Depends(get_session)
):
    """Actualiza los datos de un producto."""
    try:
        servicio = ProductoService(session)
        producto = servicio.actualizar_producto(producto_id, producto_update)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/productos/{producto_id}", tags=["Productos"])
def eliminar_producto(
    producto_id: int,
    session: Session = Depends(get_session)
):
    """Elimina un producto."""
    servicio = ProductoService(session)
    if not servicio.eliminar_producto(producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}


# ============================================================================
# CATEGORÍAS - Endpoints CRUD
# ============================================================================

@router.post("/categorias", response_model=Categoria, tags=["Categorías"])
def crear_categoria(
    categoria_data: CategoriaCreate,
    session: Session = Depends(get_session)
):
    """Crea una nueva categoría."""
    try:
        servicio = CategoriaService(session)
        return servicio.crear_categoria(categoria_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categorias/{categoria_id}", response_model=Categoria, tags=["Categorías"])
def obtener_categoria(
    categoria_id: int,
    session: Session = Depends(get_session)
):
    """Obtiene una categoría específica."""
    servicio = CategoriaService(session)
    categoria = servicio.obtener_categoria(categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.get("/categorias", response_model=list[Categoria], tags=["Categorías"])
def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Lista todas las categorías."""
    servicio = CategoriaService(session)
    return servicio.obtener_todas_categorias(skip=skip, limit=limit)


@router.put("/categorias/{categoria_id}", response_model=Categoria, tags=["Categorías"])
def actualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaUpdate,
    session: Session = Depends(get_session)
):
    """Actualiza una categoría."""
    servicio = CategoriaService(session)
    categoria = servicio.actualizar_categoria(categoria_id, categoria_update)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.delete("/categorias/{categoria_id}", tags=["Categorías"])
def eliminar_categoria(
    categoria_id: int,
    session: Session = Depends(get_session)
):
    """Elimina una categoría."""
    servicio = CategoriaService(session)
    if not servicio.eliminar_categoria(categoria_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"mensaje": "Categoría eliminada"}


# ============================================================================
# MOVIMIENTOS - Salidas y Entradas de Inventario
# ============================================================================

@router.post("/movimientos/salida", response_model=MovimientoResponse, tags=["Movimientos"])
def registrar_salida(
    producto_id: int,
    cantidad: int,
    motivo: str = None,
    usuario_id: int = None,
    session: Session = Depends(get_session)
):
    """
    Registra una salida de inventario (venta, descuento, etc).
    
    ⚠️ OPERACIÓN CRÍTICA: Se valida que no haya stock negativo.
    """
    try:
        servicio = MovimientoService(session)
        movimiento = servicio.registrar_salida(
            producto_id=producto_id,
            cantidad=cantidad,
            motivo=motivo,
            usuario_id=usuario_id
        )
        return movimiento
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/movimientos/entrada", response_model=MovimientoResponse, tags=["Movimientos"])
def registrar_entrada(
    producto_id: int,
    cantidad: int,
    motivo: str = None,
    usuario_id: int = None,
    session: Session = Depends(get_session)
):
    """
    Registra una entrada de inventario (compra, devolución, etc).
    """
    try:
        servicio = MovimientoService(session)
        movimiento = servicio.registrar_entrada(
            producto_id=producto_id,
            cantidad=cantidad,
            motivo=motivo,
            usuario_id=usuario_id
        )
        return movimiento
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/movimientos/producto/{producto_id}", response_model=list[MovimientoResponse], tags=["Movimientos"])
def historial_movimientos_producto(
    producto_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Obtiene el historial de movimientos de un producto."""
    servicio = MovimientoService(session)
    return servicio.obtener_movimientos_producto(producto_id, skip=skip, limit=limit)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", tags=["Health"])
def health_check():
    """Verifica que la API está disponible."""
    return {"status": "ok", "servicio": "SGI Backend"}
