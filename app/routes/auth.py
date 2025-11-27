"""
Rutas de autenticación: login, registro, refresh token
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from typing import Optional
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
        
        # 🔧 SINCRONIZACIÓN AUTOMÁTICA: Crear registro en estudiante/docente si corresponde
        try:
            if created_user["rol"] == "estudiante":
                # Crear registro en tabla estudiante
                estudiante_data = {
                    "ci_est": created_user["ci_user"],
                    "id_user": created_user["id_user"],
                    "carrera": "Sin especificar",
                    "semestre": 1
                }
                db.table("estudiante").insert(estudiante_data).execute()
                print(f"✅ Registro de estudiante creado automáticamente para {created_user['correo']}")
            
            elif created_user["rol"] == "docente":
                # Crear registro en tabla docente
                docente_data = {
                    "ci_doc": created_user["ci_user"],
                    "id_user": created_user["id_user"],
                    "especialidad_doc": "Sin especificar"
                }
                db.table("docente").insert(docente_data).execute()
                print(f"✅ Registro de docente creado automáticamente para {created_user['correo']}")
        except Exception as sync_error:
            # Log del error pero no fallar el registro
            print(f"⚠️  Error al sincronizar estudiante/docente: {str(sync_error)}")
        
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
        if not verify_password(form_data.password, user["contrasena"]):
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


@router.post("/validate-token")
async def validate_token(
    authorization: Optional[str] = Header(None),
    db: Client = Depends(get_db)
):
    """
    Valida un access token y retorna información sobre su estado.
    Útil para debugging en React Native.
    
    Envía el token en el header Authorization: Bearer <token>
    """
    from app.utils.security import decode_token
    from typing import Optional
    from fastapi import Header
    import logging
    
    logger = logging.getLogger(__name__)
    
    if not authorization:
        return {
            "valid": False,
            "error": "No se proporcionó token en el header Authorization"
        }
    
    # Extraer token
    token = authorization.replace('Bearer ', '').strip()
    
    # Intentar decodificar sin verificar
    payload_unverified = decode_token(token)
    
    # Verificar token
    from app.utils.security import verify_token
    payload = verify_token(token, token_type="access")
    
    if payload is None:
        # Token inválido - dar más detalles
        from datetime import datetime
        
        info = {
            "valid": False,
            "payload_unverified": payload_unverified
        }
        
        if payload_unverified:
            exp = payload_unverified.get("exp")
            if exp:
                exp_datetime = datetime.utcfromtimestamp(exp)
                now = datetime.utcnow()
                
                if exp_datetime < now:
                    tiempo_expirado = (now - exp_datetime).total_seconds()
                    info["error"] = f"Token expirado hace {tiempo_expirado/3600:.2f} horas"
                    info["expired_at"] = exp_datetime.isoformat()
                else:
                    info["error"] = "Token inválido (firma incorrecta o formato incorrecto)"
            else:
                info["error"] = "Token sin fecha de expiración"
        else:
            info["error"] = "No se pudo decodificar el token"
        
        return info
    
    # Token válido
    from datetime import datetime
    exp = payload.get("exp")
    exp_datetime = datetime.utcfromtimestamp(exp)
    now = datetime.utcnow()
    tiempo_restante = (exp_datetime - now).total_seconds()
    
    return {
        "valid": True,
        "user_id": payload.get("sub"),
        "rol": payload.get("rol"),
        "token_type": payload.get("type"),
        "expires_at": exp_datetime.isoformat(),
        "expires_in_hours": round(tiempo_restante / 3600, 2),
        "expires_in_days": round(tiempo_restante / 86400, 2)
    }
