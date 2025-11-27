"""
Rutas para gestión de publicaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client

from app.database import get_db
from app.models.social import Publicacion, PublicacionCreate, PublicacionUpdate
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/publicaciones")


@router.post("", response_model=Publicacion, status_code=status.HTTP_201_CREATED)
async def create_publicacion(
    publicacion_data: PublicacionCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Crear una nueva publicación"""
    try:
        pub_dict = publicacion_data.dict(exclude={"media_urls"})
        pub_dict["id_user"] = current_user["id_user"]
        response = db.table("publicacion").insert(pub_dict).execute()
        publicacion_id = response.data[0]["id_publicacion"]
        
        # Crear registros de media si hay URLs
        if publicacion_data.media_urls:
            for url in publicacion_data.media_urls:
                # Detectar tipo de media basado en la extensión
                tipo_media = "imagen"
                if any(ext in url.lower() for ext in ['.mp4', '.webm', '.mov', '.avi']):
                    tipo_media = "video"
                elif any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx']):
                    tipo_media = "documento"
                
                media_dict = {
                    "tipo": tipo_media,
                    "url": url,
                    "id_publicacion": publicacion_id
                }
                db.table("media").insert(media_dict).execute()
        
        # Obtener la publicación completa con información del usuario y media
        publicacion_completa = db.table("publicacion").select("*, usuario(nombre, apellido, foto_perfil), media(*)").eq("id_publicacion", publicacion_id).single().execute()
        return publicacion_completa.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[Publicacion])
async def get_publicaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener feed de publicaciones"""
    try:
        # Obtener publicaciones con información del usuario y media
        response = db.table("publicacion").select("*, usuario(nombre, apellido, foto_perfil), media(*)").order("fecha_creacion", desc=True).range(skip, skip + limit - 1).execute()
        
        # Agregar contadores de comentarios y reacciones
        publicaciones = response.data
        for pub in publicaciones:
            # Contar comentarios
            comentarios_response = db.table("comentario").select("id_comentario", count="exact").eq("id_publicacion", pub["id_publicacion"]).execute()
            pub["comentarios_count"] = comentarios_response.count or 0
            
            # Contar reacciones
            reacciones_response = db.table("reaccion").select("id_reaccion", count="exact").eq("id_publicacion", pub["id_publicacion"]).execute()
            pub["reacciones_count"] = reacciones_response.count or 0
        
        return publicaciones
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id_publicacion}", response_model=Publicacion)
async def get_publicacion(
    id_publicacion: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener una publicación por ID"""
    try:
        response = db.table("publicacion").select("*, usuario(*), media(*)").eq("id_publicacion", id_publicacion).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_publicacion}", response_model=Publicacion)
async def update_publicacion(
    id_publicacion: str,
    publicacion_data: PublicacionUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Actualizar una publicación"""
    try:
        # Verificar que es del usuario
        existing = db.table("publicacion").select("*").eq("id_publicacion", id_publicacion).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        update_data = publicacion_data.dict(exclude_unset=True)
        response = db.table("publicacion").update(update_data).eq("id_publicacion", id_publicacion).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_publicacion}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publicacion(
    id_publicacion: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Eliminar una publicación"""
    try:
        # Verificar que es del usuario
        existing = db.table("publicacion").select("*").eq("id_publicacion", id_publicacion).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        db.table("publicacion").delete().eq("id_publicacion", id_publicacion).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
