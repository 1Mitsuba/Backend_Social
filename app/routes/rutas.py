"""
Rutas para gestión de rutas de carpooling
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from supabase import Client

from app.database import get_db
from app.models.carpooling import Ruta, RutaCreate, RutaUpdate, MisRutas
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/rutas-carpooling")


@router.post("", response_model=Ruta, status_code=status.HTTP_201_CREATED)
async def create_ruta(
    ruta_data: RutaCreate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Crear una nueva ruta de carpooling"""
    try:
        ruta_dict = ruta_data.dict(exclude={"paradas"})
        ruta_dict["id_user"] = current_user["id_user"]
        response = db.table("ruta").insert(ruta_dict).execute()
        ruta = response.data[0]
        
        # Crear paradas si las hay
        if ruta_data.paradas:
            for parada in ruta_data.paradas:
                parada_dict = {
                    "orden_parada": parada.get("orden_parada"),
                    "ubicacion_parada": parada.get("ubicacion_parada"),
                    "id_ruta": ruta["id_ruta"]
                }
                db.table("parada").insert(parada_dict).execute()
        
        return ruta
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[Ruta])
async def get_rutas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    activa: bool = True,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener lista de rutas disponibles"""
    try:
        response = db.table("ruta")\
            .select("*, usuario:usuario(nombre, apellido, foto_perfil)")\
            .eq("activa", activa)\
            .order("fecha_creacion", desc=True)\
            .range(skip, skip + limit - 1)\
            .execute()
        
        # Calcular pasajeros aceptados para cada ruta
        rutas = response.data
        for ruta in rutas:
            pasajeros_response = db.table("pasajeroruta")\
                .select("*")\
                .eq("id_ruta", ruta["id_ruta"])\
                .eq("estado", "aceptado")\
                .execute()
            ruta["pasajeros_aceptados"] = len(pasajeros_response.data) if pasajeros_response.data else 0
            ruta["lugares_disponibles"] = ruta["capacidad_ruta"] - ruta["pasajeros_aceptados"]
        
        return rutas
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mis-rutas", response_model=MisRutas)
async def get_mis_rutas(
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener rutas del usuario (como conductor y pasajero)"""
    try:
        # Rutas como conductor
        conductor_response = db.table("ruta")\
            .select("*, usuario:usuario(nombre, apellido, foto_perfil)")\
            .eq("id_user", current_user["id_user"])\
            .execute()
        
        # Calcular pasajeros aceptados para cada ruta como conductor
        rutas_conductor = conductor_response.data
        for ruta in rutas_conductor:
            pasajeros_response = db.table("pasajeroruta")\
                .select("*")\
                .eq("id_ruta", ruta["id_ruta"])\
                .eq("estado", "aceptado")\
                .execute()
            ruta["pasajeros_aceptados"] = len(pasajeros_response.data) if pasajeros_response.data else 0
            ruta["lugares_disponibles"] = ruta["capacidad_ruta"] - ruta["pasajeros_aceptados"]
        
        # Rutas como pasajero
        pasajero_response = db.table("pasajeroruta")\
            .select("*, ruta:ruta(*), usuario:usuario(nombre, apellido, foto_perfil)")\
            .eq("id_user", current_user["id_user"])\
            .execute()
        
        return {
            "como_conductor": rutas_conductor,
            "como_pasajero": pasajero_response.data
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id_ruta}", response_model=Ruta)
async def get_ruta(
    id_ruta: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Obtener una ruta por ID"""
    try:
        response = db.table("ruta")\
            .select("*, usuario:usuario(*), parada:parada(*)")\
            .eq("id_ruta", id_ruta)\
            .execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada")
        
        ruta = response.data[0]
        # Calcular pasajeros aceptados
        pasajeros_response = db.table("pasajeroruta")\
            .select("*")\
            .eq("id_ruta", ruta["id_ruta"])\
            .eq("estado", "aceptado")\
            .execute()
        ruta["pasajeros_aceptados"] = len(pasajeros_response.data) if pasajeros_response.data else 0
        ruta["lugares_disponibles"] = ruta["capacidad_ruta"] - ruta["pasajeros_aceptados"]
        
        return ruta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{id_ruta}", response_model=Ruta)
async def update_ruta(
    id_ruta: str,
    ruta_data: RutaUpdate,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Actualizar una ruta"""
    try:
        # Verificar que es del conductor
        existing = db.table("ruta").select("*").eq("id_ruta", id_ruta).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        update_data = ruta_data.dict(exclude_unset=True)
        response = db.table("ruta").update(update_data).eq("id_ruta", id_ruta).execute()
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id_ruta}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ruta(
    id_ruta: str,
    db: Client = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Eliminar una ruta (desactivarla)"""
    try:
        existing = db.table("ruta").select("*").eq("id_ruta", id_ruta).execute()
        if not existing.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ruta no encontrada")
        if existing.data[0]["id_user"] != current_user["id_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        
        # Desactivar en lugar de eliminar
        db.table("ruta").update({"activa": False}).eq("id_ruta", id_ruta).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
