"""
Rutas para gestión de pasajeros en rutas de carpooling
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client
from datetime import datetime

from app.database import get_db
from app.models.carpooling import PasajeroRuta, PasajeroRutaCreate, PasajeroRutaUpdate
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/pasajeros")


@router.post("", response_model=PasajeroRuta, status_code=status.HTTP_201_CREATED)
async def postular_como_pasajero(
    pasajero_data: PasajeroRutaCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Postularse como pasajero en una ruta"""
    try:
        # Verificar que la ruta existe y está activa
        ruta = db.table("ruta").select("*").eq("id_ruta", pasajero_data.id_ruta).eq("activa", True).execute()
        if not ruta.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada o inactiva")
        
        # Verificar que no sea el conductor
        if ruta.data[0]["id_user"] == current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes ser pasajero de tu propia ruta")
        
        # Verificar que no esté ya postulado ACTIVAMENTE (pendiente o aceptado)
        existing = db.table("pasajeroruta").select("*").eq("id_ruta", pasajero_data.id_ruta).eq("id_user", current_user["id_user"]).in_("estado", ["pendiente", "aceptado"]).execute()
        if existing.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya estás postulado en esta ruta")
        
        # Crear solicitud
        pasajero_dict = pasajero_data.dict()
        pasajero_dict["id_user"] = current_user["id_user"]
        response = db.table("pasajeroruta").insert(pasajero_dict).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear solicitud de pasajero")
        
        pasajero_creado = response.data[0]
        id_pasajero_ruta = pasajero_creado.get("id_pasajero_ruta")
        
        print(f"Pasajero creado: {pasajero_creado}")
        print(f"ID Pasajero Ruta: {id_pasajero_ruta}")
        
        # Crear notificación para el conductor
        try:
            conductor_id = ruta.data[0]["id_user"]
            nombre_completo = f"{current_user.get('nombre', '')} {current_user.get('apellido', '')}".strip() or 'Un usuario'
            punto_inicio = ruta.data[0].get('punto_inicio', 'Mi ubicación actual')
            punto_destino = ruta.data[0].get('punto_destino', 'Campus Las Delicias (Univalle)')
            
            notificacion = {
                "id_user": conductor_id,
                "contenido": f"{nombre_completo} solicita unirse a tu ruta ({punto_inicio} → {punto_destino})",
                "tipo": "solicitud_ruta",
                "leida": False,
                "fecha_envio": datetime.utcnow().isoformat(),
                "id_referencia": str(id_pasajero_ruta) if id_pasajero_ruta else None
            }
            print(f"Creando notificación: {notificacion}")
            db.table("notificacion").insert(notificacion).execute()
        except Exception as e:
            print(f"Error al crear notificación: {e}")
        
        return pasajero_creado
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/ruta/{id_ruta}", response_model=List[PasajeroRuta])
async def get_pasajeros_ruta(
    id_ruta: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener pasajeros de una ruta"""
    try:
        response = db.table("pasajeroruta")\
            .select("*, usuario:usuario(nombre, apellido, foto_perfil)")\
            .eq("id_ruta", id_ruta)\
            .execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_pasajero_ruta}", response_model=PasajeroRuta)
async def update_estado_pasajero(
    id_pasajero_ruta: str,
    pasajero_data: PasajeroRutaUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Actualizar estado de un pasajero (solo conductor)"""
    try:
        # Verificar que existe
        pasajero = db.table("pasajeroruta")\
            .select("*, ruta:ruta(*)")\
            .eq("id_pasajero_ruta", id_pasajero_ruta)\
            .execute()
        if not pasajero.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
        
        # Verificar que es el conductor
        ruta = pasajero.data[0]["ruta"]
        if ruta["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el conductor puede actualizar el estado")
        
        # Actualizar estado
        update_data = pasajero_data.dict(exclude_unset=True)
        response = db.table("pasajeroruta").update(update_data).eq("id_pasajero_ruta", id_pasajero_ruta).execute()
        
        # Notificar al pasajero sobre la decisión
        try:
            pasajero_id = pasajero.data[0]["id_user"]
            estado = update_data.get("estado")
            if estado == "aceptado":
                contenido = f"¡Tu solicitud para unirte a la ruta fue aceptada! 🎉"
            elif estado == "rechazado":
                contenido = f"Tu solicitud para unirte a la ruta fue rechazada"
            else:
                contenido = None
            
            if contenido:
                notificacion = {
                    "id_user": pasajero_id,
                    "contenido": contenido,
                    "tipo": "respuesta_ruta",
                    "leida": False,
                    "fecha_envio": datetime.utcnow().isoformat()
                }
                db.table("notificacion").insert(notificacion).execute()
        except Exception as e:
            print(f"Error al crear notificación de respuesta: {e}")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_pasajero_ruta}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_solicitud(
    id_pasajero_ruta: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Cancelar solicitud de pasajero"""
    try:
        # Verificar que existe
        pasajero = db.table("pasajeroruta").select("*").eq("id_pasajero_ruta", id_pasajero_ruta).execute()
        if not pasajero.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
        
        # Solo el pasajero puede cancelar su solicitud
        if pasajero.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        # Eliminar o marcar como cancelado
        db.table("pasajeroruta").update({"estado": "cancelado"}).eq("id_pasajero_ruta", id_pasajero_ruta).execute()
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
