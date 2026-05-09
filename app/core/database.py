"""
Configuración de la base de datos
Maneja la conexión con PostgreSQL usando SQLModel
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from app.core.config import settings


# Crear motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
)


def create_db_and_tables():
    """
    Crea todas las tablas en la base de datos.
    Se ejecuta al iniciar la aplicación.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Generador de sesiones de base de datos.
    Se usa con FastAPI Dependency Injection.
    
    Yields:
        Session: Sesión de base de datos
    """
    with Session(engine) as session:
        yield session
