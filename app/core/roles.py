"""
Definición de Roles y Sistema de Permisos
Define los roles disponibles y sus permisos en el sistema
"""
from enum import Enum
from typing import List


class RolEnum(str, Enum):
    """
    Roles disponibles en el sistema.
    
    ADMIN: Acceso total, puede crear/editar/eliminar productos y usuarios
    OPERADOR: Puede registrar movimientos de stock, consultar productos
    LECTURA: Solo lectura, visualizar productos y movimientos
    """
    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"
    LECTURA = "LECTURA"


# Matriz de Permisos: qué rol puede hacer qué acción
PERMISOS_POR_ROL = {
    RolEnum.ADMIN: {
        # Productos
        "crear_producto": True,
        "actualizar_producto": True,
        "eliminar_producto": True,
        "listar_productos": True,
        "ver_producto": True,
        
        # Categorías
        "crear_categoria": True,
        "actualizar_categoria": True,
        "eliminar_categoria": True,
        "listar_categorias": True,
        
        # Movimientos
        "registrar_entrada": True,
        "registrar_salida": True,
        "ver_movimientos": True,
        
        # Usuarios
        "crear_usuario": True,
        "actualizar_usuario": True,
        "eliminar_usuario": True,
        "listar_usuarios": True,
        "cambiar_rol": True,
    },
    
    RolEnum.OPERADOR: {
        # Productos (solo lectura y operaciones de stock)
        "crear_producto": False,
        "actualizar_producto": False,
        "eliminar_producto": False,
        "listar_productos": True,
        "ver_producto": True,
        
        # Categorías (solo lectura)
        "crear_categoria": False,
        "actualizar_categoria": False,
        "eliminar_categoria": False,
        "listar_categorias": True,
        
        # Movimientos (puede registrar)
        "registrar_entrada": True,
        "registrar_salida": True,
        "ver_movimientos": True,
        
        # Usuarios (no puede gestionar)
        "crear_usuario": False,
        "actualizar_usuario": False,
        "eliminar_usuario": False,
        "listar_usuarios": False,
        "cambiar_rol": False,
    },
    
    RolEnum.LECTURA: {
        # Productos (solo lectura)
        "crear_producto": False,
        "actualizar_producto": False,
        "eliminar_producto": False,
        "listar_productos": True,
        "ver_producto": True,
        
        # Categorías (solo lectura)
        "crear_categoria": False,
        "actualizar_categoria": False,
        "eliminar_categoria": False,
        "listar_categorias": True,
        
        # Movimientos (solo lectura)
        "registrar_entrada": False,
        "registrar_salida": False,
        "ver_movimientos": True,
        
        # Usuarios (no puede gestionar)
        "crear_usuario": False,
        "actualizar_usuario": False,
        "eliminar_usuario": False,
        "listar_usuarios": False,
        "cambiar_rol": False,
    },
}


def tiene_permiso(rol: RolEnum, permiso: str) -> bool:
    """
    Verifica si un rol tiene permiso para realizar una acción.
    
    Args:
        rol: Rol del usuario
        permiso: Nombre de la acción a verificar
        
    Returns:
        bool: True si el rol tiene permiso, False en caso contrario
    """
    return PERMISOS_POR_ROL.get(rol, {}).get(permiso, False)


def obtener_permisos_rol(rol: RolEnum) -> dict:
    """
    Obtiene todos los permisos de un rol.
    
    Args:
        rol: Rol del usuario
        
    Returns:
        dict: Diccionario con todos los permisos del rol
    """
    return PERMISOS_POR_ROL.get(rol, {})
