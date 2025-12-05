"""
Rutas para gestión de estudiantes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client

from app.database import get_db
from app.models.usuario import Estudiante, EstudianteCreate, EstudianteUpdate, RolEnum
from app.utils.dependencies import get_current_active_user, require_estudiante, require_admin
from app.utils.security import get_password_hash

router = APIRouter(prefix="/estudiantes")


@router.post("", response_model=Estudiante, status_code=status.HTTP_201_CREATED)
async def create_estudiante(
    estudiante_data: EstudianteCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Crear un nuevo estudiante (solo administradores)
    """
    try:
        # Verificar que el CI no existe
        existing_ci = db.table("estudiante").select("ci_est").eq("ci_est", estudiante_data.ci_est).execute()
        if existing_ci.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El CI ya está registrado"
            )
        
        # Verificar que el correo no existe
        existing_email = db.table("usuario").select("id_user").eq("correo", estudiante_data.correo).execute()
        if existing_email.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado"
            )
        
        # Crear usuario primero
        user_dict = {
            "nombre": estudiante_data.nombre,
            "apellido": estudiante_data.apellido,
            "correo": estudiante_data.correo,
            "contrasena": get_password_hash(estudiante_data.contrasena),
            "rol": "estudiante",
            "activo": True
        }
        
        user_response = db.table("usuario").insert(user_dict).execute()
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear usuario"
            )
        
        user = user_response.data[0]
        
        # Crear estudiante
        estudiante_dict = {
            "ci_est": estudiante_data.ci_est,
            "id_user": user["id_user"],
            "carrera": estudiante_data.carrera,
            "semestre": estudiante_data.semestre,
            "id_grupo": estudiante_data.id_grupo
        }
        
        est_response = db.table("estudiante").insert(estudiante_dict).execute()
        if not est_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear estudiante"
            )
        
        estudiante = est_response.data[0]
        estudiante["usuario"] = {k: v for k, v in user.items() if k != "contrasena"}
        
        return estudiante
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear estudiante: {str(e)}"
        )


@router.get("", response_model=List[Estudiante])
async def get_estudiantes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    carrera: Optional[str] = None,
    semestre: Optional[int] = None,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtener lista de estudiantes
    """
    try:
        # Obtener estudiantes
        query = db.table("estudiante").select("*")
        
        if carrera:
            query = query.eq("carrera", carrera)
        if semestre:
            query = query.eq("semestre", semestre)
        
        query = query.range(skip, skip + limit - 1)
        estudiantes_response = query.execute()
        
        if not estudiantes_response.data:
            return []
        
        # Obtener IDs de usuario únicos
        user_ids = [est["id_user"] for est in estudiantes_response.data if est.get("id_user")]
        
        if not user_ids:
            return estudiantes_response.data
        
        # Obtener datos de usuarios
        usuarios_response = db.table("usuario").select("*").in_("id_user", user_ids).execute()
        
        # Crear mapa de usuarios
        usuarios_map = {u["id_user"]: {k: v for k, v in u.items() if k != "contrasena"} for u in usuarios_response.data}
        
        # Combinar datos
        result = []
        for est in estudiantes_response.data:
            estudiante = {**est}
            if est.get("id_user") in usuarios_map:
                estudiante["id_user"] = usuarios_map[est["id_user"]]
            result.append(estudiante)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes: {str(e)}"
        )


@router.get("/me", response_model=Estudiante)
async def get_my_estudiante_data(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtener datos de estudiante del usuario actual
    """
    if current_user["rol"] != "estudiante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo estudiantes pueden acceder a esta información"
        )
    
    try:
        # Obtener estudiante
        response = db.table("estudiante").select("*").eq("id_user", current_user["id_user"]).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Datos de estudiante no encontrados"
            )
        
        estudiante = response.data[0]
        
        # Obtener datos del usuario
        user_response = db.table("usuario").select("*").eq("id_user", current_user["id_user"]).execute()
        if user_response.data:
            usuario_data = {k: v for k, v in user_response.data[0].items() if k != "contrasena"}
            estudiante["id_user"] = usuario_data
        
        return estudiante
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener datos de estudiante: {str(e)}"
        )


@router.get("/{ci_est}", response_model=Estudiante)
async def get_estudiante(
    ci_est: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtener un estudiante por CI
    """
    try:
        # Obtener estudiante
        response = db.table("estudiante").select("*").eq("ci_est", ci_est).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado"
            )
        
        estudiante = response.data[0]
        
        # Obtener datos del usuario
        if estudiante.get("id_user"):
            user_response = db.table("usuario").select("*").eq("id_user", estudiante["id_user"]).execute()
            if user_response.data:
                usuario_data = {k: v for k, v in user_response.data[0].items() if k != "contrasena"}
                estudiante["id_user"] = usuario_data
        
        return estudiante
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiante: {str(e)}"
        )


@router.put("/{ci_est}", response_model=Estudiante)
async def update_estudiante(
    ci_est: str,
    estudiante_data: EstudianteUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Actualizar datos de un estudiante
    """
    try:
        # Verificar que existe
        existing = db.table("estudiante").select("*").eq("ci_est", ci_est).execute()
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado"
            )
        
        estudiante = existing.data[0]
        
        # Solo el mismo estudiante o un admin pueden actualizar
        if current_user["id_user"] != estudiante["id_user"] and current_user["rol"] != "administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para actualizar este estudiante"
            )
        
        # Actualizar
        update_data = estudiante_data.dict(exclude_unset=True)
        response = db.table("estudiante").update(update_data).eq("ci_est", ci_est).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar estudiante"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estudiante: {str(e)}"
        )


@router.post("/materias", status_code=status.HTTP_201_CREATED)
async def asignar_materia_estudiante(
    asignacion: dict,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Asignar una materia al grupo del estudiante (solo administradores)
    La asignación se hace a través de GrupoMateria
    """
    try:
        ci_estudiante = asignacion.get("ci_estudiante")
        id_materia = asignacion.get("id_materia")
        
        if not ci_estudiante or not id_materia:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CI de estudiante e ID de materia son requeridos"
            )
        
        # Verificar que el estudiante existe y obtener su grupo
        estudiante = db.table("estudiante").select("ci_est, id_grupo").eq("ci_est", ci_estudiante).execute()
        if not estudiante.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estudiante no encontrado"
            )
        
        id_grupo = estudiante.data[0].get("id_grupo")
        if not id_grupo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El estudiante no tiene un grupo asignado. Primero asígnale un grupo."
            )
        
        # Verificar que la materia existe
        materia = db.table("materia").select("id_materia").eq("id_materia", id_materia).execute()
        if not materia.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia no encontrada"
            )
        
        # Verificar si la materia ya está asignada al grupo
        existing = db.table("grupomateria")\
            .select("*")\
            .eq("id_grupo", id_grupo)\
            .eq("id_materia", id_materia)\
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La materia ya está asignada al grupo de este estudiante"
            )
        
        # Crear la asignación en GrupoMateria
        asignacion_data = {
            "id_grupo": id_grupo,
            "id_materia": id_materia,
            "origen": "MANUAL"
        }
        
        response = db.table("grupomateria").insert(asignacion_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al asignar materia al grupo"
            )
        
        return {
            "message": f"Materia asignada exitosamente al grupo del estudiante",
            "data": response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al asignar materia: {str(e)}"
        )
