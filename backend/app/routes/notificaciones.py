"""
Rutas para gestión de notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client

from app.database import get_db
from app.models.notificacion import Notificacion, NotificacionCreate, NotificacionesNoLeidas
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/notificaciones")


@router.post("", response_model=Notificacion, status_code=status.HTTP_201_CREATED)
async def create_notificacion(
    notif_data: NotificacionCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Crear una nueva notificación"""
    try:
        response = db.table("notificacion").insert(notif_data.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[Notificacion])
async def get_my_notificaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    leida: bool = None,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener notificaciones del usuario actual"""
    try:
        query = db.table("notificacion").select("*").eq("id_user", current_user["id_user"]).order("fecha_envio", desc=True)
        
        if leida is not None:
            query = query.eq("leida", leida)
        
        query = query.range(skip, skip + limit - 1)
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_notificacion}/leer", response_model=Notificacion)
async def marcar_notificacion_leida(
    id_notificacion: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Marcar una notificación como leída"""
    try:
        response = db.table("notificacion").update({"leida": True}).eq("id_notificacion", id_notificacion).eq("id_user", current_user["id_user"]).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/marcar-todas-leidas", status_code=status.HTTP_200_OK)
async def marcar_todas_leidas(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Marcar todas las notificaciones como leídas"""
    try:
        db.table("notificacion").update({"leida": True}).eq("id_user", current_user["id_user"]).eq("leida", False).execute()
        return {"message": "Todas las notificaciones han sido marcadas como leídas"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/no-leidas", response_model=NotificacionesNoLeidas)
async def get_notificaciones_no_leidas(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener contador de notificaciones no leídas"""
    try:
        response = db.table("notificacion").select("*").eq("id_user", current_user["id_user"]).eq("leida", False).execute()
        return {
            "total_no_leidas": len(response.data),
            "notificaciones": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_notificacion}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notificacion(
    id_notificacion: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Eliminar una notificación"""
    try:
        existing = db.table("notificacion").select("*").eq("id_notificacion", id_notificacion).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        db.table("notificacion").delete().eq("id_notificacion", id_notificacion).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
