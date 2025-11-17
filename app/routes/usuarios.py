"""
Rutas para gestión de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client
from datetime import datetime

from app.database import get_db
from app.models.usuario import (
    Usuario,
    UsuarioUpdate,
    UsuarioInDB
)
from app.utils.dependencies import (
    get_current_active_user,
    require_admin
)
from app.utils.security import get_password_hash

router = APIRouter(prefix="/usuarios")


@router.get("", response_model=List[Usuario])
async def get_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    rol: Optional[str] = None,
    activo: Optional[bool] = None,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Obtener lista de usuarios (solo administradores)
    """
    try:
        query = db.table("usuario").select("*")
        
        # Filtros opcionales
        if rol:
            query = query.eq("rol", rol)
        if activo is not None:
            query = query.eq("activo", activo)
        
        # Paginación
        query = query.range(skip, skip + limit - 1)
        
        response = query.execute()
        
        # Remover contraseñas
        usuarios = [
            {k: v for k, v in user.items() if k != "contrasena"}
            for user in response.data
        ]
        
        return usuarios
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}"
        )


@router.get("/{id_user}", response_model=Usuario)
async def get_usuario(
    id_user: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtener un usuario por ID
    """
    try:
        response = db.table("usuario").select("*").eq("id_user", id_user).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        user = response.data[0]
        
        # Solo admins o el mismo usuario pueden ver detalles completos
        if current_user["id_user"] != id_user and current_user["rol"] != "administrador":
            # Retornar solo información pública
            user = {
                "id_user": user["id_user"],
                "nombre": user["nombre"],
                "apellido": user["apellido"],
                "rol": user["rol"],
                "foto_perfil": user.get("foto_perfil")
            }
        else:
            # Remover contraseña
            user = {k: v for k, v in user.items() if k != "contrasena"}
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )


@router.put("/{id_user}", response_model=Usuario)
async def update_usuario(
    id_user: str,
    user_data: UsuarioUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Actualizar un usuario
    """
    # Solo el mismo usuario o un admin pueden actualizar
    if current_user["id_user"] != id_user and current_user["rol"] != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    
    try:
        # Verificar que el usuario existe
        existing = db.table("usuario").select("id_user").eq("id_user", id_user).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Preparar datos para actualizar (solo campos no None)
        update_data = user_data.dict(exclude_unset=True)
        
        # Si se actualiza la contraseña, hashearla
        if "contrasena" in update_data:
            update_data["contrasena"] = get_password_hash(update_data["contrasena"])
        
        # Si se actualiza el correo, verificar que no exista
        if "correo" in update_data:
            email_check = db.table("usuario").select("id_user").eq("correo", update_data["correo"]).neq("id_user", id_user).execute()
            if email_check.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo ya está en uso"
                )
        
        # Actualizar
        response = db.table("usuario").update(update_data).eq("id_user", id_user).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar usuario"
            )
        
        updated_user = response.data[0]
        
        # Remover contraseña
        user_response = {k: v for k, v in updated_user.items() if k != "contrasena"}
        
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}"
        )


@router.delete("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    id_user: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Eliminar un usuario (solo administradores)
    En realidad, solo lo desactiva
    """
    try:
        # Verificar que existe
        existing = db.table("usuario").select("id_user").eq("id_user", id_user).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Desactivar en lugar de eliminar
        db.table("usuario").update({"activo": False}).eq("id_user", id_user).execute()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuario: {str(e)}"
        )


@router.get("/search/query")
async def search_usuarios(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Buscar usuarios por nombre, apellido o correo
    """
    try:
        # Buscar en nombre, apellido o correo
        response = db.table("usuario").select("*").or_(
            f"nombre.ilike.%{q}%,apellido.ilike.%{q}%,correo.ilike.%{q}%"
        ).eq("activo", True).limit(limit).execute()
        
        if not response.data:
            return []
            
        # Retornar solo información pública
        usuarios = [
            {
                "id_user": user["id_user"],
                "nombre": user["nombre"],
                "apellido": user["apellido"],
                "correo": user["correo"],
                "rol": user["rol"],
                "foto_perfil": user.get("foto_perfil", None),
                "activo": user.get("activo", True),
                "fecha_registro": user.get("fecha_registro", datetime.now().isoformat())
            }
            for user in response.data
        ]
        
        return usuarios
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar usuarios: {str(e)}"
        )
