"""
Rutas de autenticación: login, registro, refresh token
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from supabase import Client

from app.database import get_db
from app.config import settings
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.utils.dependencies import get_current_user
from app.models.usuario import UsuarioCreate, Usuario, RolEnum

router = APIRouter(prefix="/auth")


class TokenResponse(BaseModel):
    """Respuesta del login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Usuario


class RefreshTokenRequest(BaseModel):
    """Request para refrescar token"""
    refresh_token: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UsuarioCreate,
    db: Client = Depends(get_db)
):
    """
    Registrar un nuevo usuario
    """
    try:
        # Verificar si el correo ya existe
        existing = db.table("usuario").select("id_user").eq("correo", user_data.correo).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado"
            )
        
        # Hash de la contraseña
        hashed_password = get_password_hash(user_data.contrasena)
        
        # Crear usuario
        user_dict = {
            "nombre": user_data.nombre,
            "apellido": user_data.apellido,
            "correo": user_data.correo,
            "contrasena": hashed_password,
            "rol": user_data.rol.value,
            "activo": True
        }
        
        response = db.table("usuario").insert(user_dict).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear usuario"
            )
        
        created_user = response.data[0]
        
        # Crear tokens
        access_token = create_access_token(
            data={"sub": created_user["id_user"], "rol": created_user["rol"]}
        )
        refresh_token = create_refresh_token(
            data={"sub": created_user["id_user"]}
        )
        
        # Preparar respuesta (sin contraseña)
        user_response = {k: v for k, v in created_user.items() if k != "contrasena"}
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Client = Depends(get_db)
):
    """
    Iniciar sesión (username es el correo electrónico)
    """
    try:
        # Buscar usuario por correo
        response = db.table("usuario").select("*").eq("correo", form_data.username).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = response.data[0]
        
        # Verificar contraseña
        pwd_ok = verify_password(form_data.password, user["contrasena"])

        # Si la verificación con passlib falla, intentar comparar directamente
        # con el valor almacenado (caso donde la DB tiene contraseñas en texto plano
        # o en un formato no reconocido). Si coincide, re-hashea y actualiza la fila.
        if not pwd_ok:
            stored = user.get("contrasena") or ""
            try:
                # Comparación directa (sólo como fallback para datos existentes)
                if stored and form_data.password == stored:
                    # Re-hashear con el esquema actual y actualizar registro
                    new_hash = get_password_hash(form_data.password)
                    try:
                        db.table("usuario").update({"contrasena": new_hash}).eq("id_user", user["id_user"]).execute()
                    except Exception:
                        # Si no se pudo actualizar, no interrumpimos el login; sólo logueamos
                        pass
                    pwd_ok = True
            except Exception:
                # cualquier error en fallback: tratamos como credenciales inválidas
                pwd_ok = False

        if not pwd_ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que el usuario esté activo
        if not user.get("activo", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        # Crear tokens
        access_token = create_access_token(
            data={"sub": user["id_user"], "rol": user["rol"]}
        )
        refresh_token = create_refresh_token(
            data={"sub": user["id_user"]}
        )
        
        # Preparar respuesta (sin contraseña)
        user_response = {k: v for k, v in user.items() if k != "contrasena"}
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar sesión: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Client = Depends(get_db)
):
    """
    Refrescar el access token usando el refresh token
    """
    # Verificar refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )
    
    user_id = payload.get("sub")
    
    # Obtener usuario
    try:
        response = db.table("usuario").select("*").eq("id_user", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user = response.data[0]
        
        # Verificar que esté activo
        if not user.get("activo", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )
        
        # Crear nuevos tokens
        new_access_token = create_access_token(
            data={"sub": user["id_user"], "rol": user["rol"]}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": user["id_user"]}
        )
        
        # Preparar respuesta
        user_response = {k: v for k, v in user.items() if k != "contrasena"}
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": user_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al refrescar token: {str(e)}"
        )


@router.get("/me", response_model=Usuario)
async def get_me(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener información del usuario actual
    """
    # Remover contraseña
    user_response = {k: v for k, v in current_user.items() if k != "contrasena"}
    return user_response
