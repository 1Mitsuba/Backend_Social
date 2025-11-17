"""
Rutas para gestión de reacciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client

from app.database import get_db
from app.models.social import Reaccion, ReaccionCreate
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/reacciones")


@router.post("", response_model=Reaccion, status_code=status.HTTP_201_CREATED)
async def create_reaccion(
    reaccion_data: ReaccionCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Crear o actualizar una reacción"""
    try:
        # Validar que no se proporcionen ambos IDs
        if reaccion_data.id_publicacion and reaccion_data.id_comentario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puede reaccionar a publicación y comentario al mismo tiempo"
            )
        
        # Validar que se proporcione al menos un ID
        if not reaccion_data.id_publicacion and not reaccion_data.id_comentario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar id_publicacion o id_comentario"
            )

        # Verificar si ya existe una reacción del mismo tipo
        query = db.table("reaccion").select("*").eq("id_user", current_user["id_user"]).eq("tipo_reac", reaccion_data.tipo_reac.value)
        
        if reaccion_data.id_publicacion:
            query = query.eq("id_publicacion", reaccion_data.id_publicacion)
        else:
            query = query.eq("id_comentario", reaccion_data.id_comentario)
        
        existing = query.execute()
        
        if existing.data:
            # Si ya existe, eliminarla (toggle)
            db.table("reaccion").delete().eq("id_reaccion", existing.data[0]["id_reaccion"]).execute()
            return existing.data[0]
        else:
            # Crear nueva reacción
            reac_dict = reaccion_data.dict(exclude_unset=True)
            reac_dict["id_user"] = current_user["id_user"]  # Agregar id_user del usuario autenticado
            response = db.table("reaccion").insert(reac_dict).execute()
            return response.data[0]
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/publicacion/{id_publicacion}", response_model=List[Reaccion])
async def get_reacciones_publicacion(
    id_publicacion: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener reacciones de una publicación"""
    try:
        response = db.table("reaccion").select("*").eq("id_publicacion", id_publicacion).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/comentario/{id_comentario}", response_model=List[Reaccion])
async def get_reacciones_comentario(
    id_comentario: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener reacciones de un comentario"""
    try:
        response = db.table("reaccion").select("*").eq("id_comentario", id_comentario).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_reaccion}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reaccion(
    id_reaccion: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Eliminar una reacción"""
    try:
        existing = db.table("reaccion").select("*").eq("id_reaccion", id_reaccion).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reacción no encontrada")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        db.table("reaccion").delete().eq("id_reaccion", id_reaccion).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
