"""
Rutas para gestión de amigos y solicitudes de amistad
"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from typing import List
from datetime import datetime

from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.models.relacion import (
    RelacionUsuario,
    RelacionUsuarioCreate,
    RelacionUsuarioUpdate,
    EstadoRelacionEnum
)

router = APIRouter(prefix="/amigos", tags=["amigos"])


@router.post("/solicitud", response_model=RelacionUsuario)
async def enviar_solicitud_amistad(
    id_usuario_destino: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Enviar solicitud de amistad a otro usuario"""
    try:
        # Verificar que no sea el mismo usuario
        if id_usuario_destino == current_user["id_user"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes enviarte una solicitud a ti mismo"
            )
        
        # Verificar si ya existe una relación
        existing = db.table("relacionusuario")\
            .select("*")\
            .or_(
                f"and(id_usuario1.eq.{current_user['id_user']},id_usuario2.eq.{id_usuario_destino}),"
                f"and(id_usuario1.eq.{id_usuario_destino},id_usuario2.eq.{current_user['id_user']})"
            )\
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una relación con este usuario"
            )
        
        # Crear nueva solicitud
        nueva_solicitud = {
            "id_usuario1": current_user["id_user"],
            "id_usuario2": id_usuario_destino,
            "tipo": "amistad",
            "estado": "pendiente",
            "fecha_solicitud": datetime.utcnow().isoformat()
        }
        
        response = db.table("relacionusuario").insert(nueva_solicitud).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al crear la solicitud"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/solicitudes-recibidas", response_model=List[RelacionUsuario])
async def obtener_solicitudes_recibidas(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener solicitudes de amistad recibidas pendientes"""
    try:
        response = db.table("relacionusuario")\
            .select("*, usuario1:usuario!relacionusuario_id_usuario1_fkey(id_user, nombre, apellido, foto_perfil, carrera)")\
            .eq("id_usuario2", current_user["id_user"])\
            .eq("estado", "pendiente")\
            .eq("tipo", "amistad")\
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/solicitudes-enviadas", response_model=List[RelacionUsuario])
async def obtener_solicitudes_enviadas(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener solicitudes de amistad enviadas pendientes"""
    try:
        response = db.table("relacionusuario")\
            .select("*, usuario2:usuario!relacionusuario_id_usuario2_fkey(id_user, nombre, apellido, foto_perfil, carrera)")\
            .eq("id_usuario1", current_user["id_user"])\
            .eq("estado", "pendiente")\
            .eq("tipo", "amistad")\
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/solicitud/{id_relacion}", response_model=RelacionUsuario)
async def responder_solicitud(
    id_relacion: str,
    accion: str,  # "aceptar" o "rechazar"
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Aceptar o rechazar una solicitud de amistad"""
    try:
        # Verificar que la solicitud existe y es para el usuario actual
        solicitud = db.table("relacionusuario")\
            .select("*")\
            .eq("id_relacion_usuario", id_relacion)\
            .eq("id_usuario2", current_user["id_user"])\
            .eq("estado", "pendiente")\
            .execute()
        
        if not solicitud.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )
        
        # Actualizar estado
        nuevo_estado = "aceptado" if accion == "aceptar" else "rechazado"
        
        response = db.table("relacionusuario")\
            .update({
                "estado": nuevo_estado,
                "fecha_respuesta": datetime.utcnow().isoformat()
            })\
            .eq("id_relacion_usuario", id_relacion)\
            .execute()
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/lista", response_model=List[dict])
async def obtener_amigos(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener lista de amigos aceptados"""
    try:
        # Obtener relaciones donde el usuario es usuario1
        amigos1 = db.table("relacionusuario")\
            .select("*, usuario2:usuario!relacionusuario_id_usuario2_fkey(id_user, nombre, apellido, foto_perfil, carrera, semestre)")\
            .eq("id_usuario1", current_user["id_user"])\
            .eq("estado", "aceptado")\
            .eq("tipo", "amistad")\
            .execute()
        
        # Obtener relaciones donde el usuario es usuario2
        amigos2 = db.table("relacionusuario")\
            .select("*, usuario1:usuario!relacionusuario_id_usuario1_fkey(id_user, nombre, apellido, foto_perfil, carrera, semestre)")\
            .eq("id_usuario2", current_user["id_user"])\
            .eq("estado", "aceptado")\
            .eq("tipo", "amistad")\
            .execute()
        
        # Combinar y formatear resultados
        amigos = []
        
        for relacion in amigos1.data:
            if relacion.get('usuario2'):
                amigo = relacion['usuario2']
                amigos.append({
                    "id_relacion": relacion['id_relacion_usuario'],
                    "id_user": amigo['id_user'],
                    "nombre": amigo['nombre'],
                    "apellido": amigo.get('apellido', ''),
                    "foto_perfil": amigo.get('foto_perfil'),
                    "carrera": amigo.get('carrera'),
                    "semestre": amigo.get('semestre'),
                    "fecha_amistad": relacion.get('fecha_respuesta')
                })
        
        for relacion in amigos2.data:
            if relacion.get('usuario1'):
                amigo = relacion['usuario1']
                amigos.append({
                    "id_relacion": relacion['id_relacion_usuario'],
                    "id_user": amigo['id_user'],
                    "nombre": amigo['nombre'],
                    "apellido": amigo.get('apellido', ''),
                    "foto_perfil": amigo.get('foto_perfil'),
                    "carrera": amigo.get('carrera'),
                    "semestre": amigo.get('semestre'),
                    "fecha_amistad": relacion.get('fecha_respuesta')
                })
        
        return amigos
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/eliminar/{id_relacion}")
async def eliminar_amigo(
    id_relacion: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Eliminar un amigo"""
    try:
        # Verificar que la relación existe y pertenece al usuario
        relacion = db.table("relacionusuario")\
            .select("*")\
            .eq("id_relacion_usuario", id_relacion)\
            .or_(f"id_usuario1.eq.{current_user['id_user']},id_usuario2.eq.{current_user['id_user']}")\
            .execute()
        
        if not relacion.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relación no encontrada"
            )
        
        # Eliminar relación
        db.table("relacionusuario")\
            .delete()\
            .eq("id_relacion_usuario", id_relacion)\
            .execute()
        
        return {"message": "Amigo eliminado exitosamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
