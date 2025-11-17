"""
Rutas para gestión de comentarios
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client

from app.database import get_db
from app.models.social import Comentario, ComentarioCreate, ComentarioUpdate
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/comentarios")


@router.post("", response_model=Comentario, status_code=status.HTTP_201_CREATED)
async def create_comentario(
    comentario_data: ComentarioCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Crear un nuevo comentario"""
    try:
        com_dict = comentario_data.dict()
        com_dict["id_user"] = current_user["id_user"]
        response = db.table("comentario").insert(com_dict).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/publicacion/{id_publicacion}", response_model=List[Comentario])
async def get_comentarios_publicacion(
    id_publicacion: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener comentarios de una publicación"""
    try:
        response = db.table("comentario").select("*, usuario(nombre, apellido, foto_perfil)").eq("id_publicacion", id_publicacion).order("fecha_creacion", desc=True).range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_comentario}", response_model=Comentario)
async def update_comentario(
    id_comentario: str,
    comentario_data: ComentarioUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Actualizar un comentario"""
    try:
        existing = db.table("comentario").select("*").eq("id_comentario", id_comentario).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        update_data = comentario_data.dict(exclude_unset=True)
        response = db.table("comentario").update(update_data).eq("id_comentario", id_comentario).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_comentario}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comentario(
    id_comentario: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Eliminar un comentario"""
    try:
        existing = db.table("comentario").select("*").eq("id_comentario", id_comentario).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comentario no encontrado")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        db.table("comentario").delete().eq("id_comentario", id_comentario).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
