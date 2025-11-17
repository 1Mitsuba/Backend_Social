"""
Rutas para gestión de mensajes y conversaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from supabase import Client

from app.database import get_db
from app.models.mensajeria import (
    Conversacion, ConversacionCreate,
    Mensaje, MensajeCreate,
    MensajesNoLeidos
)
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/mensajes")


@router.post("/conversaciones", response_model=Conversacion, status_code=status.HTTP_201_CREATED)
async def create_conversacion(
    conv_data: ConversacionCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Crear una nueva conversación"""
    try:
        # Verificar que el usuario actual no esté en la lista (se agregará automáticamente)
        participantes = [p for p in conv_data.participantes if p != current_user["id_user"]]
        
        # Agregar el usuario actual a la lista de participantes si no está
        if current_user["id_user"] not in participantes:
            participantes.append(current_user["id_user"])
            
        # Verificar que haya al menos otro participante además del usuario actual
        if len(participantes) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar al menos un participante además del usuario actual"
            )

        # Crear conversación
        conv_dict = {"tipo": conv_data.tipo.value, "nombre": conv_data.nombre}
        response = db.table("conversacion").insert(conv_dict).execute()
        conversacion = response.data[0]
        
        # Agregar participantes
        for id_usuario in participantes:
            user_conv = {
                "id_usuario": id_usuario,
                "id_conversacion": conversacion["id_conversacion"],
                "rol": "admin" if id_usuario == current_user["id_user"] else "miembro"
            }
            db.table("usuarioconversacion").insert(user_conv).execute()
        
        return conversacion
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/conversaciones", response_model=List[Conversacion])
async def get_my_conversaciones(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener conversaciones del usuario actual"""
    try:
        # Obtener directamente las conversaciones donde el usuario actual es participante
        query = db.table("usuarioconversacion")\
            .select(
                "conversacion:conversacion(*), usuario:usuario(id_user, nombre, apellido, foto_perfil)"
            )\
            .eq("id_usuario", current_user["id_user"])\
            .execute()

        if not query.data:
            return []

        # Procesar las conversaciones
        resultado = []
        conv_processed = set()  # Para evitar duplicados

        for item in query.data:
            if not item.get("conversacion") or item["conversacion"]["id_conversacion"] in conv_processed:
                continue

            conv = item["conversacion"]
            conv_id = conv["id_conversacion"]
            conv_processed.add(conv_id)

            # Obtener otros participantes
            otros_participantes = db.table("usuarioconversacion")\
                .select("usuario:usuario(id_user, nombre, apellido, foto_perfil)")\
                .eq("id_conversacion", conv_id)\
                .execute()

            conv["participantes"] = [
                p["usuario"] for p in otros_participantes.data 
                if p.get("usuario") and p["usuario"]["id_user"] != current_user["id_user"]
            ]

            # Obtener último mensaje
            ultimo_mensaje = db.table("mensaje")\
                .select("*, usuario:usuario(nombre, apellido)")\
                .eq("id_conversacion", conv_id)\
                .order("fecha_envio", desc=True)\
                .limit(1)\
                .execute()

            conv["ultimo_mensaje"] = ultimo_mensaje.data[0] if ultimo_mensaje.data else None

            # Contar mensajes no leídos
            mensajes_no_leidos = db.table("mensaje")\
                .select("id_mensaje")\
                .eq("id_conversacion", conv_id)\
                .eq("leido", False)\
                .neq("id_user", current_user["id_user"])\
                .execute()

            conv["mensajes_no_leidos"] = len(mensajes_no_leidos.data)

            resultado.append(conv)

        return resultado
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=Mensaje, status_code=status.HTTP_201_CREATED)
async def send_mensaje(
    mensaje_data: MensajeCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Enviar un mensaje"""
    try:
        msg_dict = mensaje_data.dict()
        msg_dict["id_user"] = current_user["id_user"]
        response = db.table("mensaje").insert(msg_dict).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/conversacion/{id_conversacion}", response_model=List[Mensaje])
async def get_mensajes_conversacion(
    id_conversacion: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener mensajes de una conversación"""
    try:
        # Verificar que el usuario está en la conversación
        user_conv = db.table("usuarioconversacion").select("*").eq("id_conversacion", id_conversacion).eq("id_usuario", current_user["id_user"]).execute()
        if not user_conv.data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta conversación")
        
        # Obtener mensajes
        response = db.table("mensaje")\
            .select("*, usuario:usuario(nombre, apellido, foto_perfil)")\
            .eq("id_conversacion", id_conversacion)\
            .order("fecha_envio")\
            .range(skip, skip + limit - 1)\
            .execute()
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_mensaje}/leer", response_model=Mensaje)
async def marcar_mensaje_leido(
    id_mensaje: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Marcar un mensaje como leído"""
    try:
        response = db.table("mensaje").update({"leido": True}).eq("id_mensaje", id_mensaje).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/no-leidos", response_model=MensajesNoLeidos)
async def get_mensajes_no_leidos(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener contador de mensajes no leídos"""
    try:
        # Obtener conversaciones del usuario
        user_convs = db.table("usuarioconversacion").select("id_conversacion").eq("id_usuario", current_user["id_user"]).execute()
        conv_ids = [uc["id_conversacion"] for uc in user_convs.data]
        
        if not conv_ids:
            return {"total_no_leidos": 0, "conversaciones": []}
        
        # Contar mensajes no leídos
        response = db.table("mensaje").select("*").in_("id_conversacion", conv_ids).eq("leido", False).neq("id_user", current_user["id_user"]).execute()
        
        return {
            "total_no_leidos": len(response.data),
            "conversaciones": []  # TODO: agrupar por conversación
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
