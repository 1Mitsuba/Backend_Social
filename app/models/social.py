"""
Modelos Pydantic para el módulo social (publicaciones, comentarios, reacciones)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============= PUBLICACIÓN =============

class TipoPublicacionEnum(str, Enum):
    """Tipos de publicación"""
    TEXTO = "texto"
    IMAGEN = "imagen"
    DOCUMENTO = "documento"
    ENLACE = "enlace"
    RUTA_CARPOOLING = "ruta_carpooling"


class PublicacionBase(BaseModel):
    """Modelo base de publicación"""
    contenido: str = Field(..., min_length=1)
    tipo: TipoPublicacionEnum


class PublicacionCreate(PublicacionBase):
    """Modelo para crear una publicación"""
    id_user: Optional[str] = None  # Opcional, se asigna automáticamente desde el token JWT
    media_urls: Optional[List[str]] = []  # URLs de archivos multimedia


class PublicacionUpdate(BaseModel):
    """Modelo para actualizar una publicación"""
    contenido: Optional[str] = Field(None, min_length=1)


class Publicacion(PublicacionBase):
    """Modelo de publicación para respuestas"""
    id_publicacion: str
    id_user: str
    fecha_creacion: datetime
    usuario: Optional[dict] = None  # Información del usuario
    media: Optional[List[dict]] = []  # Lista de archivos multimedia
    comentarios_count: Optional[int] = 0
    reacciones_count: Optional[int] = 0
    mis_reacciones: Optional[List[str]] = []  # Reacciones del usuario actual

    class Config:
        from_attributes = True


# ============= COMENTARIO =============

class ComentarioBase(BaseModel):
    """Modelo base de comentario"""
    contenido: str = Field(..., min_length=1)
    id_publicacion: str


class ComentarioCreate(ComentarioBase):
    """Modelo para crear un comentario"""
    id_user: Optional[str] = None  # Opcional, se asigna automáticamente desde el token JWT


class ComentarioUpdate(BaseModel):
    """Modelo para actualizar un comentario"""
    contenido: Optional[str] = Field(None, min_length=1)


class Comentario(ComentarioBase):
    """Modelo de comentario para respuestas"""
    id_comentario: str
    id_user: str
    fecha_creacion: datetime
    usuario: Optional[dict] = None  # Información del usuario

    class Config:
        from_attributes = True


# ============= MEDIA =============

class TipoMediaEnum(str, Enum):
    """Tipos de archivos multimedia"""
    IMAGEN = "imagen"
    VIDEO = "video"
    DOCUMENTO = "documento"
    AUDIO = "audio"


class MediaBase(BaseModel):
    """Modelo base de media"""
    tipo: TipoMediaEnum
    url: str = Field(..., max_length=500)
    id_publicacion: str


class MediaCreate(MediaBase):
    """Modelo para crear un archivo multimedia"""
    pass


class Media(MediaBase):
    """Modelo de media para respuestas"""
    id_media: str

    class Config:
        from_attributes = True


# ============= COMENTARIO =============

class ComentarioBase(BaseModel):
    """Modelo base de comentario"""
    contenido: str = Field(..., min_length=1)
    id_publicacion: str


class ComentarioCreate(ComentarioBase):
    """Modelo para crear un comentario"""
    id_user: str


class ComentarioUpdate(BaseModel):
    """Modelo para actualizar un comentario"""
    contenido: Optional[str] = Field(None, min_length=1)


class Comentario(ComentarioBase):
    """Modelo de comentario para respuestas"""
    id_comentario: str
    id_user: str
    fecha_creacion: datetime
    usuario: Optional[dict] = None  # Información del usuario
    reacciones_count: Optional[int] = 0
    mis_reacciones: Optional[List[str]] = []  # Reacciones del usuario actual

    class Config:
        from_attributes = True


# ============= REACCIÓN =============

class TipoReaccionEnum(str, Enum):
    """Tipos de reacción"""
    LIKE = "like"
    DISLIKE = "dislike"
    LOVE = "love"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"


class ReaccionBase(BaseModel):
    """Modelo base de reacción"""
    tipo_reac: TipoReaccionEnum


class ReaccionCreate(ReaccionBase):
    """Modelo para crear una reacción"""
    id_publicacion: Optional[str] = None
    id_comentario: Optional[str] = None
    
    @validator('id_comentario')
    def validate_target(cls, v, values):
        """Validar que se proporcione publicación o comentario, pero no ambos"""
        id_publicacion = values.get('id_publicacion')
        if not id_publicacion and not v:
            raise ValueError('Debe proporcionar id_publicacion o id_comentario')
        if id_publicacion and v:
            raise ValueError('No puede reaccionar a publicación y comentario al mismo tiempo')
        return v


class Reaccion(ReaccionBase):
    """Modelo de reacción para respuestas"""
    id_reaccion: str
    id_user: str
    id_publicacion: Optional[str] = None
    id_comentario: Optional[str] = None
    fecha_creacion_reac: datetime
    usuario: Optional[dict] = None  # Información del usuario

    class Config:
        from_attributes = True


# ============= MODELOS DE RESPUESTA AGREGADOS =============

class PublicacionConDetalles(Publicacion):
    """Publicación con comentarios y reacciones"""
    comentarios: List[Comentario] = []
    reacciones: List[Reaccion] = []
