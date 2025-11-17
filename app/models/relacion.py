"""
Modelos Pydantic para relaciones entre usuarios (amistades)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


# ============= RELACIÓN USUARIO =============

class TipoRelacionEnum(str, Enum):
    """Tipos de relación"""
    AMISTAD = "amistad"
    BLOQUEADO = "bloqueado"


class EstadoRelacionEnum(str, Enum):
    """Estados de relación"""
    PENDIENTE = "pendiente"
    ACEPTADO = "aceptado"
    RECHAZADO = "rechazado"


class RelacionUsuarioBase(BaseModel):
    """Modelo base de relación entre usuarios"""
    tipo: TipoRelacionEnum = TipoRelacionEnum.AMISTAD
    estado: EstadoRelacionEnum = EstadoRelacionEnum.PENDIENTE


class RelacionUsuarioCreate(RelacionUsuarioBase):
    """Modelo para crear una relación"""
    id_usuario1: str  # Usuario que envía la solicitud
    id_usuario2: str  # Usuario que recibe la solicitud
    
    @validator('id_usuario2')
    def validate_usuarios(cls, v, values):
        """Validar que los usuarios sean diferentes"""
        if 'id_usuario1' in values and v == values['id_usuario1']:
            raise ValueError('No puedes crear una relación contigo mismo')
        return v


class RelacionUsuarioUpdate(BaseModel):
    """Modelo para actualizar una relación"""
    estado: EstadoRelacionEnum
    tipo: Optional[TipoRelacionEnum] = None


class RelacionUsuario(RelacionUsuarioBase):
    """Modelo de relación para respuestas"""
    id_relacion_usuario: str
    id_usuario1: str
    id_usuario2: str
    fecha_solicitud: datetime
    fecha_respuesta: Optional[datetime] = None
    usuario1: Optional[dict] = None  # Información del usuario 1
    usuario2: Optional[dict] = None  # Información del usuario 2

    class Config:
        from_attributes = True


# ============= MODELOS DE RESPUESTA AGREGADOS =============

class SolicitudesAmistad(BaseModel):
    """Solicitudes de amistad pendientes"""
    enviadas: list[RelacionUsuario] = []
    recibidas: list[RelacionUsuario] = []


class Amigos(BaseModel):
    """Lista de amigos"""
    amigos: list[dict] = []  # Lista de usuarios amigos
    total: int = 0
