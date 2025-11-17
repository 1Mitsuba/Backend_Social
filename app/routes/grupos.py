"""
Rutas para gestión de grupos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client

from app.database import get_db
from app.models.academico import Grupo, GrupoCreate, GrupoUpdate
from app.utils.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/grupos")


@router.post("", response_model=Grupo, status_code=status.HTTP_201_CREATED)
async def create_grupo(
    grupo_data: GrupoCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Crear un nuevo grupo"""
    try:
        response = db.table("grupo").insert(grupo_data.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[Grupo])
async def get_grupos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener lista de grupos"""
    try:
        response = db.table("grupo").select("*").range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id_grupo}", response_model=Grupo)
async def get_grupo(
    id_grupo: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener un grupo por ID"""
    try:
        response = db.table("grupo").select("*").eq("id_grupo", id_grupo).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_grupo}", response_model=Grupo)
async def update_grupo(
    id_grupo: str,
    grupo_data: GrupoUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Actualizar un grupo"""
    try:
        update_data = grupo_data.dict(exclude_unset=True)
        response = db.table("grupo").update(update_data).eq("id_grupo", id_grupo).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
