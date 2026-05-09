"""
Configuración global de la aplicación
Valores por defecto, reglas de negocio y parámetros del sistema
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación.
    Todas las variables se cargan desde .env para mantener seguridad y flexibilidad.
    """
    
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost/sgi_db"
    DB_ECHO: bool = False  # Muestra las queries SQL en logs (útil en desarrollo)
    
    # Aplicación
    APP_TITLE: str = "SGI - Sistema de Gestión de Inventario"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Reglas de negocio
    STOCK_MINIMO_ALERTA: int = 10  # Umbral para alertar stock bajo
    STOCK_MINIMO_PERMITIDO: int = 0  # Stock mínimo que no puede ser negativo
    
    # Tipos de movimiento válidos
    TIPOS_MOVIMIENTO_VALIDOS: list = ["ENTRADA", "SALIDA", "AJUSTE", "TRANSFERENCIA"]
    
    # Seguridad
    SECRET_KEY: str = "tu-clave-secreta-muy-segura"  # Cambiar en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json o text
    
    # Paginación
    PAGE_SIZE_DEFAULT: int = 20
    PAGE_SIZE_MAX: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
