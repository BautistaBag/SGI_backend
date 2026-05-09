"""
Seguridad - Hashing, JWT y Autenticación
Maneja contraseñas, tokens y autenticación
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings

# Contexto para hashing de contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# HASHING DE CONTRASEÑAS
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash una contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Contraseña hasheada
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada almacenada
        
    Returns:
        bool: True si la contraseña es correcta
    """
    return pwd_context.verify(plain_password, hashed_password)


def validar_politica_contrasena(password: str) -> tuple[bool, str]:
    """
    Valida que una contraseña cumpla con la política de seguridad.
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    
    Args:
        password: Contraseña a validar
        
    Returns:
        tuple: (es_válida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe tener al menos una mayúscula"
    
    if not any(c.islower() for c in password):
        return False, "La contraseña debe tener al menos una minúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe tener al menos un número"
    
    especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in especiales for c in password):
        return False, f"La contraseña debe tener al menos un carácter especial: {especiales}"
    
    return True, ""


# ============================================================================
# JWT - JSON WEB TOKENS
# ============================================================================

def crear_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un JWT con los datos del usuario.
    
    Args:
        data: Datos a codificar (ej: usuario_id, rol)
        expires_delta: Tiempo de expiración (default: 30 minutos)
        
    Returns:
        str: Token JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verificar_token(token: str) -> Optional[dict]:
    """
    Verifica y decodifica un JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        dict: Datos del token si es válido, None si no lo es
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ============================================================================
# GESTIÓN DE INTENTOS FALLIDOS
# ============================================================================

# En un sistema real, esto estaría en Redis o la BD
# Por ahora lo hacemos en memoria (se pierde al reiniciar)
intentos_fallidos = {}
INTENTOS_MAX = 5
BLOQUEO_MINUTOS = 15


def registrar_intento_fallido(usuario_email: str):
    """
    Registra un intento fallido de login.
    Si excede el máximo, bloquea temporalmente la cuenta.
    
    Args:
        usuario_email: Email del usuario
    """
    if usuario_email not in intentos_fallidos:
        intentos_fallidos[usuario_email] = {
            "intentos": 0,
            "bloqueado_hasta": None
        }
    
    record = intentos_fallidos[usuario_email]
    record["intentos"] += 1
    
    if record["intentos"] >= INTENTOS_MAX:
        record["bloqueado_hasta"] = datetime.utcnow() + timedelta(
            minutes=BLOQUEO_MINUTOS
        )


def limpiar_intentos_fallidos(usuario_email: str):
    """
    Limpia los intentos fallidos después de un login exitoso.
    
    Args:
        usuario_email: Email del usuario
    """
    if usuario_email in intentos_fallidos:
        intentos_fallidos[usuario_email] = {
            "intentos": 0,
            "bloqueado_hasta": None
        }


def esta_bloqueado(usuario_email: str) -> tuple[bool, Optional[str]]:
    """
    Verifica si una cuenta está bloqueada temporalmente.
    
    Args:
        usuario_email: Email del usuario
        
    Returns:
        tuple: (está_bloqueado, motivo)
    """
    if usuario_email not in intentos_fallidos:
        return False, None
    
    record = intentos_fallidos[usuario_email]
    
    if record["bloqueado_hasta"] and datetime.utcnow() < record["bloqueado_hasta"]:
        tiempo_restante = (record["bloqueado_hasta"] - datetime.utcnow()).seconds // 60
        return True, f"Cuenta bloqueada. Intente en {tiempo_restante} minutos"
    
    # Desbloquear si el tiempo de bloqueo expiró
    if record["bloqueado_hasta"] and datetime.utcnow() >= record["bloqueado_hasta"]:
        limpiar_intentos_fallidos(usuario_email)
    
    return False, None
