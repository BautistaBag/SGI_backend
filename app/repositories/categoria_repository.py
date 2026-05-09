"""
Repositorio de Categoría
Contiene consultas específicas para la tabla 'categoria'
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.models.categoria import Categoria
from app.repositories.base_repository import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    """
    Repositorio específico para operaciones con categorías.
    """
    
    def __init__(self, session: Session):
        super().__init__(session, Categoria)
    
    def get_by_nombre(self, nombre: str) -> Optional[Categoria]:
        """
        Obtiene una categoría por nombre.
        
        Args:
            nombre: Nombre de la categoría
            
        Returns:
            Categoria: Categoría encontrada o None
        """
        statement = select(Categoria).where(Categoria.nombre == nombre)
        return self.session.exec(statement).first()
    
    def get_activas(self, skip: int = 0, limit: int = 100) -> List[Categoria]:
        """
        Obtiene solo las categorías activas.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            List[Categoria]: Lista de categorías activas
        """
        statement = (
            select(Categoria)
            .where(Categoria.activa == True)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()
