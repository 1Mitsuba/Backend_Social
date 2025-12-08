"""
Rutas para gestión de horarios
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import datetime
from supabase import Client

from app.database import get_db
from app.models.academico import Horario, HorarioCreate, HorarioUpdate
from app.utils.dependencies import get_current_active_user, require_docente_or_admin

router = APIRouter(prefix="/horarios")


@router.post("", response_model=Horario, status_code=status.HTTP_201_CREATED)
async def create_horario(
    horario_data: HorarioCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Crear un nuevo horario"""
    try:
        response = db.table("horario").insert(horario_data.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mi-horario", response_model=List[Horario])
async def get_my_horario(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener horario del estudiante actual con información de materias"""
    if current_user["rol"] != "estudiante":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo para estudiantes")
    
    try:
        # Obtener grupo del estudiante
        est_response = db.table("estudiante").select("id_grupo").eq("id_user", current_user["id_user"]).execute()
        if not est_response.data or not est_response.data[0].get("id_grupo"):
            return []
        
        id_grupo = est_response.data[0]["id_grupo"]
        
        # Obtener horarios del grupo
        response = db.table("horario").select("*").eq("id_grupo", id_grupo).order("dia_semana, hora_inicio").execute()
        
        # Obtener todas las materias del grupo con sus datos completos
        materias_response = db.table("grupomateria").select("*, materia(*)").eq("id_grupo", id_grupo).execute()
        materias_list = [gm["materia"] for gm in materias_response.data if gm.get("materia")]
        
        # Agregar información de materias a cada horario
        horarios = []
        for h in response.data:
            horario = dict(h)
            # Si hay materias, añadir la lista completa para que el frontend elija
            if materias_list:
                horario["materias"] = materias_list
                # Por compatibilidad, también añadir la primera como "materia"
                horario["materia"] = materias_list[0] if materias_list else None
            else:
                horario["materias"] = []
                horario["materia"] = None
            horarios.append(horario)
        
        return horarios
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/grupo/{id_grupo}", response_model=List[Horario])
async def get_horario_grupo(
    id_grupo: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener horarios de un grupo específico con información de materias"""
    try:
        # Obtener horarios del grupo
        response = db.table("horario").select("*").eq("id_grupo", id_grupo).order("dia_semana, hora_inicio").execute()
        
        # Obtener todas las materias del grupo con sus datos completos
        materias_response = db.table("grupomateria").select("*, materia(*)").eq("id_grupo", id_grupo).execute()
        materias_list = [gm["materia"] for gm in materias_response.data if gm.get("materia")]
        
        # Agregar información de materias a cada horario
        horarios = []
        for h in response.data:
            horario = dict(h)
            if materias_list:
                horario["materias"] = materias_list
                horario["materia"] = materias_list[0] if materias_list else None
            else:
                horario["materias"] = []
                horario["materia"] = None
            horarios.append(horario)
        
        return horarios
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/estudiante/{ci_est}", response_model=List[Horario])
async def get_horario_estudiante(
    ci_est: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener horarios de un estudiante por su CI con información de materias"""
    try:
        # Obtener grupo del estudiante
        est_response = db.table("estudiante").select("id_grupo").eq("ci_est", ci_est).execute()
        if not est_response.data or not est_response.data[0].get("id_grupo"):
            return []
        
        id_grupo = est_response.data[0]["id_grupo"]
        
        # Obtener horarios del grupo
        response = db.table("horario").select("*").eq("id_grupo", id_grupo).order("dia_semana, hora_inicio").execute()
        
        # Obtener todas las materias del grupo con sus datos completos
        materias_response = db.table("grupomateria").select("*, materia(*)").eq("id_grupo", id_grupo).execute()
        materias_list = [gm["materia"] for gm in materias_response.data if gm.get("materia")]
        
        # Agregar información de materias a cada horario
        horarios = []
        for h in response.data:
            horario = dict(h)
            if materias_list:
                horario["materias"] = materias_list
                horario["materia"] = materias_list[0] if materias_list else None
            else:
                horario["materias"] = []
                horario["materia"] = None
            horarios.append(horario)
        
        return horarios
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            horarios.append(horario)
        
        return horarios
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_horario}", response_model=Horario)
async def update_horario(
    id_horario: str,
    horario_data: HorarioUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Actualizar un horario"""
    try:
        # Primero verificamos si el horario existe
        existing = db.table("horario").select("*").eq("id_horario", id_horario).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horario no encontrado")

        # Convertir el modelo a diccionario y asegurarse de que los campos de tiempo sean strings
        update_data = {}
        data_dict = horario_data.model_dump(exclude_unset=True)
        
        # Procesar cada campo y asegurarse de que los campos de tiempo sean strings
        for field, value in data_dict.items():
            if field in ['hora_inicio', 'hora_fin'] and value is not None:
                # Asegurarse de que las horas estén en formato string HH:MM:SS
                if isinstance(value, str):
                    # Limpiar el formato ISO si existe
                    if 'Z' in value:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        update_data[field] = dt.strftime('%H:%M:%S')
                    else:
                        # Validar que el formato sea correcto
                        try:
                            datetime.strptime(value, '%H:%M:%S')
                            update_data[field] = value
                        except ValueError:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Formato inválido para {field}. Use HH:MM:SS"
                            )
            else:
                update_data[field] = value

        # Realizar la actualización
        response = db.table("horario").update(update_data).eq("id_horario", id_horario).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_horario}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_horario(
    id_horario: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_docente_or_admin)
):
    """Eliminar un horario"""
    try:
        db.table("horario").delete().eq("id_horario", id_horario).execute()
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
