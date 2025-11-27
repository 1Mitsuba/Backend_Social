"""
Rutas para gestión de materias
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client

from app.database import get_db
from app.models.academico import Materia, MateriaCreate, MateriaUpdate
from app.utils.dependencies import get_current_active_user, require_docente_or_admin

router = APIRouter(prefix="/materias")


@router.post("", response_model=Materia, status_code=status.HTTP_201_CREATED)
async def create_materia(
    materia_data: MateriaCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Crear una nueva materia"""
    try:
        response = db.table("materia").insert(materia_data.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[Materia])
async def get_materias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener lista de materias con información del docente"""
    try:
        # Incluir información del docente y su usuario
        response = db.table("materia").select("*, docente:id_doc(ci_doc, usuario:id_user(*))").range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mis-materias", response_model=List[Materia])
async def get_my_materias(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener materias del estudiante actual"""
    if current_user["rol"] != "estudiante":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo para estudiantes")
    
    try:
        # Obtener grupo del estudiante
        est_response = db.table("estudiante").select("id_grupo").eq("id_user", current_user["id_user"]).execute()
        if not est_response.data or not est_response.data[0].get("id_grupo"):
            return []
        
        id_grupo = est_response.data[0]["id_grupo"]
        
        # Obtener materias del grupo
        response = db.table("grupomateria").select("Materia(*)").eq("id_grupo", id_grupo).execute()
        materias = [item["Materia"] for item in response.data if item.get("Materia")]
        return materias
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id_materia}", response_model=Materia)
async def get_materia(
    id_materia: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener una materia por ID"""
    try:
        response = db.table("materia").select("*").eq("id_materia", id_materia).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_materia}", response_model=Materia)
async def update_materia(
    id_materia: str,
    materia_data: MateriaUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Actualizar una materia"""
    try:
        update_data = materia_data.dict(exclude_unset=True)
        response = db.table("materia").update(update_data).eq("id_materia", id_materia).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia no encontrada")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
