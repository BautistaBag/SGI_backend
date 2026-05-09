"""
Punto de entrada de FastAPI
Configuración de la aplicación y enrutamiento
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.routes import router
from app.api.auth import router as auth_router

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Sistema de Gestión de Inventario con arquitectura por capas",
    debug=settings.DEBUG
)

# ============================================================================
# MIDDLEWARE - CORS
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# EVENTOS DE STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
def on_startup():
    """Se ejecuta al iniciar la aplicación."""
    print("✅ Iniciando SGI Backend...")
    print(f"📚 Creando tablas de base de datos...")
    create_db_and_tables()
    print(f"✅ {settings.APP_TITLE} iniciada")


@app.on_event("shutdown")
def on_shutdown():
    """Se ejecuta al apagar la aplicación."""
    print("🛑 SGI Backend se está deteniendo...")


# ============================================================================
# RUTAS
# ============================================================================
app.include_router(router)
app.include_router(auth_router)


# ============================================================================
# ENDPOINT RAÍZ
# ============================================================================

@app.get("/")
def root():
    """Endpoint raíz que describe la API."""
    return {
        "titulo": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "endpoints": {
            "documentación": "/docs",
            "documentación-openapi": "/openapi.json",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
