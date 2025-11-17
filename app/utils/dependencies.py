"""
Dependencias reutilizables para FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from app.database import get_db
from app.utils.security import verify_token
from supabase import Client

# Esquema de seguridad Bearer
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db)
) -> dict:
    """
    Obtiene el usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales de autorización (token)
        db: Cliente de base de datos
        
    Returns:
        Diccionario con datos del usuario
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Verificar token
    token = credentials.credentials
    logger.debug(f"Token recibido: {token[:30]}...")
    
    # Asegurarse de que el token no tenga 'Bearer' incluido
    if token.startswith('Bearer '):
        token = token.replace('Bearer ', '')
        logger.warning("Se detectó 'Bearer' en el token, removiendo...")
    
    payload = verify_token(token, token_type="access")
    logger.info(f"Resultado de verificación: {payload}")
    
    if payload is None:
        logger.warning("Token inválido o expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extraer ID de usuario del payload
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener usuario de la base de datos
    try:
        response = db.table("usuario").select("*").eq("id_user", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user = response.data[0]
        
        # Verificar que el usuario esté activo
        if not user.get("activo", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Verifica que el usuario actual esté activo
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario si está activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.get("activo", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def require_role(allowed_roles: List[str]):
    """
    Dependencia para requerir roles específicos
    
    Args:
        allowed_roles: Lista de roles permitidos
        
    Returns:
        Función de dependencia que verifica el rol
    """
    async def role_checker(
        current_user: dict = Depends(get_current_active_user)
    ) -> dict:
        """
        Verifica que el usuario tenga uno de los roles permitidos
        """
        user_role = current_user.get("rol")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado. Se requiere rol: {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


# Dependencias pre-configuradas para roles comunes
require_estudiante = require_role(["estudiante"])
require_docente = require_role(["docente"])
require_admin = require_role(["administrador"])
require_docente_or_admin = require_role(["docente", "administrador"])
