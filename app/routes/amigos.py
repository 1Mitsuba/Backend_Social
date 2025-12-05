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
        
        # Crear notificación para el destinatario
        try:
            # Obtener el nombre completo del usuario
            nombre_completo = f"{current_user.get('nombre', '')} {current_user.get('apellido', '')}".strip() or 'Un usuario'
            notificacion = {
                "id_user": id_usuario_destino,
                "contenido": f"{nombre_completo} te envió una solicitud de amistad",
                "tipo": "solicitud_amistad",
                "leida": False,
                "fecha_envio": datetime.utcnow().isoformat(),
                "id_referencia": response.data[0].get('id_relacion_usuario')
            }
            db.table("notificacion").insert(notificacion).execute()
        except Exception as e:
            print(f"Error al crear notificación: {e}")
        
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
            .select("*")\
            .eq("id_usuario2", current_user["id_user"])\
            .eq("estado", "pendiente")\
            .eq("tipo", "amistad")\
            .execute()
        
        # Obtener datos de los usuarios que enviaron las solicitudes
        solicitudes = []
        for rel in response.data:
            usuario = db.table("usuario")\
                .select("id_user, nombre, apellido, correo, rol, foto_perfil")\
                .eq("id_user", rel["id_usuario1"])\
                .execute()
            
            if usuario.data:
                rel["usuario1"] = usuario.data[0]
                solicitudes.append(rel)
        
        return solicitudes
    except Exception as e:
        print(f"Error en obtener_solicitudes_recibidas: {e}")
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
            .select("*")\
            .eq("id_usuario1", current_user["id_user"])\
            .eq("estado", "pendiente")\
            .eq("tipo", "amistad")\
            .execute()
        
        # Obtener datos de los usuarios a quienes se enviaron las solicitudes
        solicitudes = []
        for rel in response.data:
            usuario = db.table("usuario")\
                .select("id_user, nombre, apellido, correo, rol, foto_perfil")\
                .eq("id_user", rel["id_usuario2"])\
                .execute()
            
            if usuario.data:
                rel["usuario2"] = usuario.data[0]
                solicitudes.append(rel)
        
        return solicitudes
    except Exception as e:
        print(f"Error en obtener_solicitudes_enviadas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
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
        
        # Crear notificación si se aceptó
        if accion == "aceptar":
            try:
                # Obtener el nombre completo del usuario
                nombre_completo = f"{current_user.get('nombre', '')} {current_user.get('apellido', '')}".strip() or 'Un usuario'
                notificacion = {
                    "id_user": solicitud.data[0]['id_usuario1'],
                    "contenido": f"{nombre_completo} aceptó tu solicitud de amistad",
                    "tipo": "amistad_aceptada",
                    "leida": False,
                    "fecha_envio": datetime.utcnow().isoformat(),
                    "id_referencia": id_relacion
                }
                db.table("notificacion").insert(notificacion).execute()
            except Exception as e:
                print(f"Error al crear notificación: {e}")
        
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
        print(f"Obteniendo amigos para usuario: {current_user['id_user']}")
        
        # Obtener relaciones donde el usuario es usuario1
        amigos1 = db.table("relacionusuario")\
            .select("*")\
            .eq("id_usuario1", current_user["id_user"])\
            .eq("estado", "aceptado")\
            .eq("tipo", "amistad")\
            .execute()
        
        print(f"Amigos1 encontrados: {len(amigos1.data)}")
        
        # Obtener relaciones donde el usuario es usuario2
        amigos2 = db.table("relacionusuario")\
            .select("*")\
            .eq("id_usuario2", current_user["id_user"])\
            .eq("estado", "aceptado")\
            .eq("tipo", "amistad")\
            .execute()
        
        print(f"Amigos2 encontrados: {len(amigos2.data)}")
        
        # Combinar y formatear resultados
        amigos = []
        
        for relacion in amigos1.data:
            usuario = db.table("usuario")\
                .select("id_user, nombre, apellido, correo, rol, foto_perfil")\
                .eq("id_user", relacion["id_usuario2"])\
                .execute()
            
            if usuario.data:
                amigo = usuario.data[0]
                amigos.append({
                    "id_relacion": relacion['id_relacion_usuario'],
                    "id_user": amigo['id_user'],
                    "nombre": amigo['nombre'],
                    "apellido": amigo.get('apellido', ''),
                    "correo": amigo.get('correo', ''),
                    "rol": amigo.get('rol', ''),
                    "foto_perfil": amigo.get('foto_perfil'),
                    "fecha_amistad": relacion.get('fecha_respuesta')
                })
        
        for relacion in amigos2.data:
            usuario = db.table("usuario")\
                .select("id_user, nombre, apellido, correo, rol, foto_perfil")\
                .eq("id_user", relacion["id_usuario1"])\
                .execute()
            
            if usuario.data:
                amigo = usuario.data[0]
                amigos.append({
                    "id_relacion": relacion['id_relacion_usuario'],
                    "id_user": amigo['id_user'],
                    "nombre": amigo['nombre'],
                    "apellido": amigo.get('apellido', ''),
                    "correo": amigo.get('correo', ''),
                    "rol": amigo.get('rol', ''),
                    "foto_perfil": amigo.get('foto_perfil'),
                    "fecha_amistad": relacion.get('fecha_respuesta')
                })
        
        print(f"Total amigos formateados: {len(amigos)}")
        return amigos
    
    except Exception as e:
        print(f"Error en obtener_amigos: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
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


@router.get("/buscar")
async def buscar_usuarios(
    q: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Buscar usuarios por nombre, apellido o correo"""
    try:
        print(f"Buscando usuarios con query: {q}")
        print(f"Usuario actual: {current_user['id_user']}")
        
        # Buscar usuarios - usar ilike con porcentajes en el valor
        usuarios = db.table("usuario")\
            .select("id_user, nombre, apellido, correo, rol, foto_perfil")\
            .neq("id_user", current_user["id_user"])\
            .or_(f"nombre.ilike.*{q}*,apellido.ilike.*{q}*,correo.ilike.*{q}*")\
            .limit(20)\
            .execute()
        
        print(f"Usuarios encontrados: {len(usuarios.data)}")
        
        # Obtener todas las relaciones del usuario actual
        relaciones = db.table("relacionusuario")\
            .select("id_usuario1, id_usuario2, estado")\
            .or_(f"id_usuario1.eq.{current_user['id_user']},id_usuario2.eq.{current_user['id_user']}")\
            .execute()
        
        # Crear un mapa de estados de relación
        estados_relacion = {}
        for rel in relaciones.data:
            if rel['id_usuario1'] == current_user['id_user']:
                estados_relacion[rel['id_usuario2']] = rel['estado']
            else:
                estados_relacion[rel['id_usuario1']] = rel['estado']
        
        # Agregar estado de relación a cada usuario
        resultado = []
        for usuario in usuarios.data:
            usuario_con_estado = dict(usuario)
            usuario_con_estado['estadoRelacion'] = estados_relacion.get(usuario['id_user'])
            resultado.append(usuario_con_estado)
        
        return resultado
    
    except Exception as e:
        print(f"Error en buscar_usuarios: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
