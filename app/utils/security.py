"""
Utilidades de seguridad: hash de contraseñas, JWT, etc.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from passlib.exc import UnknownHashError
import logging

# Contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña
        
    Returns:
        True si coinciden, False si no
    """
    logger = logging.getLogger(__name__)
    if not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError as e:
        # Hash almacenado no reconocido por passlib (ej. migración desde otro sistema)
        logger.warning("verify_password: unknown hash format for user password: %s", str(e))
        return False
    except Exception as e:
        # Cualquier otro error en la verificación no debe provocar 500; tratamos como credenciales inválidas
        logger.exception("verify_password: unexpected error while verifying password: %s", str(e))
        return False


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso
    
    Args:
        data: Datos a codificar en el token
        expires_delta: Tiempo de expiración del token
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de refresco
    
    Args:
        data: Datos a codificar en el token
        expires_delta: Tiempo de expiración del token
        
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token: Token JWT a verificar (sin el prefijo 'Bearer')
        token_type: Tipo de token esperado ("access" o "refresh")
        
    Returns:
        Payload del token si es válido, None si no
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Remover 'Bearer' si está presente
    if token.startswith('Bearer '):
        token = token.replace('Bearer ', '')
        logger.warning("'Bearer' detectado en el token y removido")
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

    except Exception as e:
        # Log detallado para depuración: fallo al decodificar/verificar firma
        # No registramos el token completo para evitar exposición accidental en logs.
        short_token = (token[:8] + "..." + token[-8:]) if token and len(token) > 32 else token
        logger.debug("verify_token: jwt.decode failed for token=%s error=%s", short_token, str(e))
        return None

    # Verificar tipo de token
    if payload.get("type") != token_type:
        logger.debug("verify_token: token type mismatch, expected=%s got=%s", token_type, payload.get("type"))
        return None

    # Verificar expiración (usar UTC para evitar errores por zonas horarias)
    exp = payload.get("exp")
    if exp is None:
        logger.debug("verify_token: token has no 'exp' claim")
        return None

    # Comparar usando timestamps en UTC (aware)
    try:
        exp_dt = datetime.fromtimestamp(exp, timezone.utc)
    except Exception as e:
        logger.debug("verify_token: invalid 'exp' claim value=%s error=%s", str(exp), str(e))
        return None

    if exp_dt < datetime.now(timezone.utc):
        logger.debug("verify_token: token expired at %s (now=%s)", exp_dt.isoformat(), datetime.now(timezone.utc).isoformat())
        return None

    logger.debug("verify_token: token valid for sub=%s type=%s exp=%s", payload.get("sub"), payload.get("type"), exp_dt.isoformat())
    return payload


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica un token JWT sin verificar su validez
    (útil para debugging)
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload del token o None si hay error
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_signature": False}
        )
    except JWTError:
        return None
