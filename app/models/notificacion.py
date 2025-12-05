"""
Modelos Pydantic para notificaciones
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ============= NOTIFICACIÓN =============

class TipoNotificacionEnum(str, Enum):
    """Tipos de notificación"""
    COMENTARIO = "comentario"
    REACCION = "reaccion"
    SOLICITUD_AMISTAD = "solicitud_amistad"
    AMISTAD_ACEPTADA = "amistad_aceptada"
    SOLICITUD_RUTA = "solicitud_ruta"
    MENSAJE = "mensaje"
    NOTA_NUEVA = "nota_nueva"
    OTRO = "otro"


class NotificacionBase(BaseModel):
    """Modelo base de notificación"""
    contenido: str = Field(..., min_length=1)
    tipo: str


class NotificacionCreate(NotificacionBase):
    """Modelo para crear una notificación"""
    id_user: str  # Usuario que recibe la notificación


class NotificacionUpdate(BaseModel):
    """Modelo para actualizar una notificación"""
    leida: bool


class Notificacion(NotificacionBase):
    """Modelo de notificación para respuestas"""
    id_notificacion: str
    id_user: str
    fecha_envio: datetime
    leida: bool = False
    id_referencia: Optional[str] = None

    class Config:
        from_attributes = True


# ============= MODELOS DE RESPUESTA AGREGADOS =============

class NotificacionesNoLeidas(BaseModel):
    """Contador de notificaciones no leídas"""
    total_no_leidas: int
    notificaciones: list[Notificacion] = []
