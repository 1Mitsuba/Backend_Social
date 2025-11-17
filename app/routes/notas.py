"""
Rutas para gestión de notas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client

from app.database import get_db
from app.models.academico import Nota, NotaCreate, NotaUpdate
from app.utils.dependencies import get_current_active_user, require_docente_or_admin

router = APIRouter(prefix="/notas")


@router.post("", response_model=Nota, status_code=status.HTTP_201_CREATED)
async def create_nota(
    nota_data: NotaCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Crear una nueva nota"""
    try:
        response = db.table("nota").insert(nota_data.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mis-notas", response_model=List[Nota])
async def get_my_notas(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener notas del estudiante actual"""
    if current_user["rol"] != "estudiante":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo para estudiantes")
    
    try:
        response = db.table("nota").select("*, materia(*)").eq("id_user", current_user["id_user"]).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/estudiante/{id_user}", response_model=List[Nota])
async def get_notas_estudiante(
    id_user: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Obtener notas de un estudiante específico"""
    try:
        response = db.table("nota").select("*, materia(*)").eq("id_user", id_user).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_nota}", response_model=Nota)
async def update_nota(
    id_nota: str,
    nota_data: NotaUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Actualizar una nota"""
    try:
        update_data = nota_data.dict(exclude_unset=True)
        response = db.table("nota").update(update_data).eq("id_nota", id_nota).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_nota}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nota(
    id_nota: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Eliminar una nota"""
    try:
        db.table("nota").delete().eq("id_nota", id_nota).execute()
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
