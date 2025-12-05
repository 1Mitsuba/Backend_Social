"""
Modelos Pydantic para el módulo de carpooling
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, time
from enum import Enum


# ============= RUTA =============

class RutaBase(BaseModel):
    """Modelo base de ruta de carpooling"""
    punto_inicio: str = Field(..., min_length=3, max_length=200)
    punto_destino: str = Field(..., min_length=3, max_length=200)
    hora_salida: str = Field(..., pattern=r'^\d{2}:\d{2}:\d{2}$')  # Formato HH:MM:SS
    dias_disponibles: str = Field(..., max_length=100)  # Ej: "Lunes,Martes,Viernes"
    capacidad_ruta: int = Field(..., ge=1, le=8)
    
    @validator('dias_disponibles')
    def validate_dias(cls, v):
        """Validar formato de días disponibles"""
        dias_validos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dias = [d.strip() for d in v.split(',')]
        for dia in dias:
            if dia not in dias_validos:
                raise ValueError(f'Día inválido: {dia}. Días válidos: {", ".join(dias_validos)}')
        return v


class RutaCreate(RutaBase):
    """Modelo para crear una ruta"""
    paradas: Optional[List[dict]] = []  # Lista de paradas intermedias


class RutaUpdate(BaseModel):
    """Modelo para actualizar una ruta"""
    punto_inicio: Optional[str] = Field(None, min_length=3, max_length=200)
    punto_destino: Optional[str] = Field(None, min_length=3, max_length=200)
    hora_salida: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}:\d{2}$')
    dias_disponibles: Optional[str] = Field(None, max_length=100)
    capacidad_ruta: Optional[int] = Field(None, ge=1, le=8)
    activa: Optional[bool] = None


class Ruta(RutaBase):
    """Modelo de ruta para respuestas"""
    id_ruta: str
    id_user: str
    fecha_creacion: datetime
    activa: bool = True
    conductor: Optional[dict] = None  # Información del conductor
    paradas: Optional[List[dict]] = []  # Lista de paradas
    pasajeros_count: Optional[int] = 0
    pasajeros_aceptados: Optional[int] = 0
    lugares_disponibles: Optional[int] = 0

    class Config:
        from_attributes = True


# ============= PARADA =============

class ParadaBase(BaseModel):
    """Modelo base de parada"""
    orden_parada: int = Field(..., ge=1)
    ubicacion_parada: str = Field(..., min_length=3, max_length=200)
    id_ruta: str


class ParadaCreate(ParadaBase):
    """Modelo para crear una parada"""
    pass


class ParadaUpdate(BaseModel):
    """Modelo para actualizar una parada"""
    orden_parada: Optional[int] = Field(None, ge=1)
    ubicacion_parada: Optional[str] = Field(None, min_length=3, max_length=200)


class Parada(ParadaBase):
    """Modelo de parada para respuestas"""
    id_parada: str

    class Config:
        from_attributes = True


# ============= PASAJERO RUTA =============

class EstadoPasajeroEnum(str, Enum):
    """Estados de pasajero en ruta"""
    PENDIENTE = "pendiente"
    ACEPTADO = "aceptado"
    RECHAZADO = "rechazado"
    CANCELADO = "cancelado"


class PasajeroRutaBase(BaseModel):
    """Modelo base de pasajero en ruta"""
    id_ruta: str
    estado: EstadoPasajeroEnum = EstadoPasajeroEnum.PENDIENTE


class PasajeroRutaCreate(BaseModel):
    """Modelo para postular como pasajero"""
    id_ruta: str
    estado: EstadoPasajeroEnum = EstadoPasajeroEnum.PENDIENTE


class PasajeroRutaUpdate(BaseModel):
    """Modelo para actualizar estado de pasajero"""
    estado: EstadoPasajeroEnum

class PasajeroRuta(PasajeroRutaBase):
    """Modelo de pasajero-ruta para respuestas"""
    id_pasajero_ruta: str
    id_user: str
    fecha_union: datetime
    pasajero: Optional[dict] = None  # Información del pasajero
    ruta: Optional[dict] = None  # Información de la ruta

    class Config:
        from_attributes = True
        from_attributes = True


# ============= MODELOS DE RESPUESTA AGREGADOS =============

class RutaConDetalles(Ruta):
    """Ruta con pasajeros y paradas completas"""
    pasajeros: List[PasajeroRuta] = []
    paradas_completas: List[Parada] = []


class MisRutas(BaseModel):
    """Rutas del usuario (como conductor y pasajero)"""
    como_conductor: List[Ruta] = []
    como_pasajero: List[PasajeroRuta] = []
