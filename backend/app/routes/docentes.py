"""
Rutas para gestión de docentes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client

from app.database import get_db
from app.models.usuario import Docente, DocenteCreate, DocenteUpdate
from app.utils.dependencies import get_current_active_user, require_admin
from app.utils.security import get_password_hash

router = APIRouter(prefix="/docentes")


@router.post("", response_model=Docente, status_code=status.HTTP_201_CREATED)
async def create_docente(
    docente_data: DocenteCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Crear un nuevo docente (solo administradores)
    """
    try:
        # Verificar que el CI no existe
        existing_ci = db.table("docente").select("ci_doc").eq("ci_doc", docente_data.ci_doc).execute()
        if existing_ci.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El CI ya está registrado"
            )
        
        # Verificar que el correo no existe
        existing_email = db.table("usuario").select("id_user").eq("correo", docente_data.correo).execute()
        if existing_email.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado"
            )
        
        # Crear usuario primero
        user_dict = {
            "nombre": docente_data.nombre,
            "apellido": docente_data.apellido,
            "correo": docente_data.correo,
            "contrasena": get_password_hash(docente_data.contrasena),
            "rol": "docente",
            "activo": True
        }
        
        user_response = db.table("usuario").insert(user_dict).execute()
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear usuario"
            )
        
        user = user_response.data[0]
        
        # Crear docente
        docente_dict = {
            "ci_doc": docente_data.ci_doc,
            "id_user": user["id_user"],
            "especialidad_doc": docente_data.especialidad_doc
        }
        
        doc_response = db.table("docente").insert(docente_dict).execute()
        if not doc_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear docente"
            )
        
        docente = doc_response.data[0]
        docente["usuario"] = {k: v for k, v in user.items() if k != "contrasena"}
        
        return docente
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear docente: {str(e)}"
        )


@router.get("")
async def get_docentes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    especialidad: Optional[str] = None,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtener lista de docentes
    """
    try:
        # Primero obtener los docentes
        query = db.table("docente").select("*")
        
        if especialidad:
            query = query.eq("especialidad_doc", especialidad)
            
        docentes_response = query.range(skip, skip + limit - 1).execute()
        
        if not docentes_response.data:
            return []
            
        # Obtener los IDs de usuario
        user_ids = [doc["id_user"] for doc in docentes_response.data]
        
        # Obtener los datos de usuario correspondientes
        usuarios_response = db.table("usuario").select("*").in_("id_user", user_ids).execute()
        
        if not usuarios_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener datos de usuarios"
            )
            
        # Crear un diccionario para mapear usuarios por ID
        usuarios_map = {user["id_user"]: user for user in usuarios_response.data}
        
        # Combinar los datos
        docentes = []
        for doc in docentes_response.data:
            usuario = usuarios_map.get(doc["id_user"])
            if usuario:
                # Remover contraseña del usuario
                usuario_data = {k: v for k, v in usuario.items() if k != "contrasena"}
                docente_data = {
                    **doc,
                    "usuario": usuario_data
                }
                docentes.append(docente_data)
                
        return docentes
        query = db.table("docente").select("*, Usuario(*)")
        
        if especialidad:
            query = query.eq("especialidad_doc", especialidad)
        
        query = query.range(skip, skip + limit - 1)
        response = query.execute()
        
        return response.data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener docentes: {str(e)}"
        )


@router.get("/me", response_model=Docente)
async def get_my_docente_data(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtener datos de docente del usuario actual
    """
    if current_user["rol"] != "docente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docentes pueden acceder a esta información"
        )
    
    try:
        response = db.table("docente").select("*, Usuario(*)").eq("id_user", current_user["id_user"]).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Datos de docente no encontrados"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener datos de docente: {str(e)}"
        )


@router.get("/{ci_doc}")
async def get_docente(
    ci_doc: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Obtener un docente por CI
    """
    try:
        # Obtener el docente
        docente_response = db.table("docente").select("*").eq("ci_doc", ci_doc).execute()
        
        if not docente_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente no encontrado"
            )
            
        docente = docente_response.data[0]
        
        # Obtener los datos del usuario asociado
        user_response = db.table("usuario").select("*").eq("id_user", docente["id_user"]).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario asociado no encontrado"
            )
            
        usuario = user_response.data[0]
        
        # Remover contraseña del usuario
        usuario_data = {k: v for k, v in usuario.items() if k != "contrasena"}
        
        # Combinar los datos
        return {
            **docente,
            "usuario": usuario_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener docente: {str(e)}"
        )


@router.put("/{ci_doc}")
async def update_docente(
    ci_doc: str,
    docente_data: DocenteUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Actualizar datos de un docente
    """
    try:
        # 1. Verificar que el docente existe
        doc_response = db.table("docente").select("*").eq("ci_doc", ci_doc).execute()
        if not doc_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente no encontrado"
            )
            
        docente = doc_response.data[0]
        
        # 2. Verificar permisos
        if current_user["id_user"] != docente["id_user"] and current_user["rol"] != "administrador":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para actualizar este docente"
            )
        
        # 3. Actualizar el docente
        update_data = {}
        if docente_data.especialidad_doc is not None:
            update_data["especialidad_doc"] = docente_data.especialidad_doc
            
        if update_data:
            update_response = db.table("docente").update(update_data).eq("ci_doc", ci_doc).execute()
            if not update_response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al actualizar docente"
                )
            docente = update_response.data[0]
        
        # 4. Obtener datos del usuario asociado
        user_response = db.table("usuario").select("*").eq("id_user", docente["id_user"]).execute()
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario asociado no encontrado"
            )
            
        usuario = user_response.data[0]
        usuario_data = {k: v for k, v in usuario.items() if k != "contrasena"}
        
        # 5. Retornar datos actualizados
        return {
            **docente,
            "usuario": usuario_data
        }
        
        # Actualizar
        update_data = docente_data.dict(exclude_unset=True)
        response = db.table("docente").update(update_data).eq("ci_doc", ci_doc).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar docente"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar docente: {str(e)}"
        )
