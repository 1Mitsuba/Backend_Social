"""
Modelos Pydantic para el módulo de mensajería
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============= CONVERSACIÓN =============

class TipoConversacionEnum(str, Enum):
    """Tipos de conversación"""
    PRIVADA = "privada"
    GRUPAL = "grupal"


class ConversacionBase(BaseModel):
    """Modelo base de conversación"""
    tipo: TipoConversacionEnum
    nombre: Optional[str] = Field(None, max_length=150)
    
    @validator('nombre')
    def validate_nombre(cls, v, values):
        """Validar que conversaciones grupales tengan nombre"""
        if values.get('tipo') == TipoConversacionEnum.GRUPAL and not v:
            raise ValueError('Las conversaciones grupales deben tener un nombre')
        return v


class ConversacionCreate(ConversacionBase):
    """Modelo para crear una conversación"""
    participantes: List[str] = Field(..., min_items=2)  # IDs de usuarios


class ConversacionUpdate(BaseModel):
    """Modelo para actualizar una conversación"""
    nombre: Optional[str] = Field(None, max_length=150)


class Conversacion(ConversacionBase):
    """Modelo de conversación para respuestas"""
    id_conversacion: str
    fecha_creacion: datetime
    participantes: Optional[List[dict]] = []  # Lista de usuarios participantes
    ultimo_mensaje: Optional[dict] = None  # Último mensaje de la conversación
    mensajes_no_leidos: Optional[int] = 0

    class Config:
        from_attributes = True


# ============= USUARIO CONVERSACIÓN =============

class RolConversacionEnum(str, Enum):
    """Roles en conversación"""
    ADMIN = "admin"
    MIEMBRO = "miembro"


class UsuarioConversacionBase(BaseModel):
    """Modelo base de usuario en conversación"""
    id_usuario: str
    id_conversacion: str
    rol: RolConversacionEnum = RolConversacionEnum.MIEMBRO


class UsuarioConversacionCreate(UsuarioConversacionBase):
    """Modelo para agregar un usuario a una conversación"""
    pass


class UsuarioConversacionUpdate(BaseModel):
    """Modelo para actualizar rol de usuario en conversación"""
    rol: Optional[RolConversacionEnum] = None


class UsuarioConversacion(UsuarioConversacionBase):
    """Modelo de usuario-conversación para respuestas"""
    id_usuario_conversacion: str
    fecha_union: datetime
    usuario: Optional[dict] = None  # Información del usuario

    class Config:
        from_attributes = True


# ============= MENSAJE =============

class MensajeBase(BaseModel):
    """Modelo base de mensaje"""
    contenido: str = Field(..., min_length=1)
    id_conversacion: str


class MensajeCreate(MensajeBase):
    """Modelo para crear un mensaje"""
    id_user: Optional[str] = None  # Opcional, se toma del token JWT


class MensajeUpdate(BaseModel):
    """Modelo para actualizar un mensaje"""
    contenido: Optional[str] = Field(None, min_length=1)
    leido: Optional[bool] = None


class Mensaje(MensajeBase):
    """Modelo de mensaje para respuestas"""
    id_mensaje: str
    id_user: str
    fecha_envio: datetime
    leido: bool = False
    usuario: Optional[dict] = None  # Información del usuario

    class Config:
        from_attributes = True


# ============= MODELOS DE RESPUESTA AGREGADOS =============

class ConversacionConMensajes(Conversacion):
    """Conversación con lista de mensajes"""
    mensajes: List[Mensaje] = []


class MensajesNoLeidos(BaseModel):
    """Contador de mensajes no leídos"""
    total_no_leidos: int
    conversaciones: List[dict]  # Lista de conversaciones con mensajes no leídos
