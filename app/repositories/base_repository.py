"""
Repositorio Base
Contiene operaciones CRUD genéricas reutilizables por todos los repositorios
"""
from typing import TypeVar, Generic, Type, Optional, List
from sqlmodel import Session, select

T = TypeVar('T')  # Tipo genérico para el modelo


class BaseRepository(Generic[T]):
    """
    Repositorio genérico con operaciones CRUD básicas.
    Todos los repositorios específicos heredan de esta clase.
    """
    
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model
    
    def create(self, obj: T) -> T:
        """
        Crea un nuevo registro.
        
        Args:
            obj: Objeto del modelo a crear
            
        Returns:
            T: Objeto creado con ID asignado
        """
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Obtiene un registro por ID.
        
        Args:
            id: ID del registro
            
        Returns:
            T: Objeto encontrado o None
        """
        return self.session.get(self.model, id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Obtiene todos los registros con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            
        Returns:
            List[T]: Lista de objetos
        """
        statement = select(self.model).offset(skip).limit(limit)
        return self.session.exec(statement).all()
    
    def update(self, id: int, obj_update: dict) -> Optional[T]:
        """
        Actualiza un registro existente.
        
        Args:
            id: ID del registro
            obj_update: Diccionario con campos a actualizar
            
        Returns:
            T: Objeto actualizado o None
        """
        obj = self.get_by_id(id)
        if not obj:
            return None
        
        for key, value in obj_update.items():
            if value is not None:
                setattr(obj, key, value)
        
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    
    def delete(self, id: int) -> bool:
        """
        Elimina un registro.
        
        Args:
            id: ID del registro
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        obj = self.get_by_id(id)
        if not obj:
            return False
        
        self.session.delete(obj)
        self.session.commit()
        return True
