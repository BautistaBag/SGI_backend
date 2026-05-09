"""
Servicio de Categoría
Contiene la lógica de negocio para operaciones con categorías
"""
from typing import Optional, List
from sqlmodel import Session
from app.models.categoria import Categoria, CategoriaCreate, CategoriaUpdate
from app.repositories.categoria_repository import CategoriaRepository


class CategoriaService:
    """
    Servicio que orquesta la lógica de negocio para categorías.
    """
    
    def __init__(self, session: Session):
        self.session = session
        self.categoria_repo = CategoriaRepository(session)
    
    def crear_categoria(self, categoria_data: CategoriaCreate) -> Categoria:
        """
        Crea una nueva categoría.
        
        Args:
            categoria_data: Datos de la categoría
            
        Returns:
            Categoria: Categoría creada
            
        Raises:
            ValueError: Si el nombre ya existe
        """
        # Validar nombre único
        existente = self.categoria_repo.get_by_nombre(categoria_data.nombre)
        if existente:
            raise ValueError(f"Categoría '{categoria_data.nombre}' ya existe")
        
        nueva_categoria = Categoria(**categoria_data.dict())
        return self.categoria_repo.create(nueva_categoria)
    
    def actualizar_categoria(
        self, 
        categoria_id: int, 
        categoria_update: CategoriaUpdate
    ) -> Optional[Categoria]:
        """Actualiza una categoría."""
        return self.categoria_repo.update(categoria_id, categoria_update.dict(exclude_unset=True))
    
    def obtener_categoria(self, categoria_id: int) -> Optional[Categoria]:
        """Obtiene una categoría por ID."""
        return self.categoria_repo.get_by_id(categoria_id)
    
    def obtener_todas_categorias(self, skip: int = 0, limit: int = 20) -> List[Categoria]:
        """Obtiene todas las categorías."""
        return self.categoria_repo.get_all(skip=skip, limit=limit)
    
    def obtener_categorias_activas(self, skip: int = 0, limit: int = 20) -> List[Categoria]:
        """Obtiene solo categorías activas."""
        return self.categoria_repo.get_activas(skip=skip, limit=limit)
    
    def eliminar_categoria(self, categoria_id: int) -> bool:
        """Elimina una categoría."""
        return self.categoria_repo.delete(categoria_id)
