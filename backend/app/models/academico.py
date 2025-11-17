"""
Modelos Pydantic para el módulo académico
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime, date, time
from enum import Enum


# ============= GESTIÓN ACADÉMICA =============

class EstadoGestionEnum(str, Enum):
    """Estados de gestión académica"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    FINALIZADO = "finalizado"


class GestionAcademicaBase(BaseModel):
    """Modelo base de gestión académica"""
    nombre_gestion: str = Field(..., min_length=3, max_length=50)
    fecha_inicio: date
    fecha_fin: date
    estado: EstadoGestionEnum = EstadoGestionEnum.ACTIVO
    
    @validator('fecha_fin')
    def validate_dates(cls, v, values):
        if 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class GestionAcademicaCreate(GestionAcademicaBase):
    """Modelo para crear una gestión académica"""
    pass


class GestionAcademicaUpdate(BaseModel):
    """Modelo para actualizar una gestión académica"""
    nombre_gestion: Optional[str] = Field(None, min_length=3, max_length=50)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[EstadoGestionEnum] = None


class GestionAcademica(GestionAcademicaBase):
    """Modelo de gestión académica para respuestas"""
    id_gestion: str

    class Config:
        from_attributes = True


# ============= GRUPO =============

class GrupoBase(BaseModel):
    """Modelo base de grupo"""
    nombre_grupo: str = Field(..., min_length=1, max_length=100)
    gestion_grupo: str


class GrupoCreate(GrupoBase):
    """Modelo para crear un grupo"""
    pass


class GrupoUpdate(BaseModel):
    """Modelo para actualizar un grupo"""
    nombre_grupo: Optional[str] = Field(None, min_length=1, max_length=100)
    gestion_grupo: Optional[str] = None


class Grupo(GrupoBase):
    """Modelo de grupo para respuestas"""
    id_grupo: str

    class Config:
        from_attributes = True


# ============= MATERIA =============

class OrigenEnum(str, Enum):
    """Origen de los datos"""
    SIU = "SIU"
    MANUAL = "MANUAL"


class MateriaBase(BaseModel):
    """Modelo base de materia"""
    nombre_materia: str = Field(..., min_length=3, max_length=150)
    codigo_materia: str = Field(..., min_length=3, max_length=20)
    id_doc: Optional[str] = None
    origen: OrigenEnum = OrigenEnum.SIU


class MateriaCreate(MateriaBase):
    """Modelo para crear una materia"""
    pass


class MateriaUpdate(BaseModel):
    """Modelo para actualizar una materia"""
    nombre_materia: Optional[str] = Field(None, min_length=3, max_length=150)
    codigo_materia: Optional[str] = Field(None, min_length=3, max_length=20)
    id_doc: Optional[str] = None


class Materia(MateriaBase):
    """Modelo de materia para respuestas"""
    id_materia: str
    docente: Optional[dict] = None  # Información del docente si existe

    class Config:
        from_attributes = True


# ============= GRUPO MATERIA =============

class GrupoMateriaBase(BaseModel):
    """Modelo base de grupo-materia"""
    id_grupo: str
    id_materia: str
    origen: OrigenEnum = OrigenEnum.SIU


class GrupoMateriaCreate(GrupoMateriaBase):
    """Modelo para crear una relación grupo-materia"""
    pass


class GrupoMateria(GrupoMateriaBase):
    """Modelo de grupo-materia para respuestas"""
    id_grupo_materia: str

    class Config:
        from_attributes = True


# ============= NOTA =============

class NotaBase(BaseModel):
    """Modelo base de nota"""
    nota: float = Field(..., ge=0, le=100)
    tipo_nota: str = Field(..., min_length=2, max_length=50)
    id_user: str
    id_materia: str
    origen: OrigenEnum = OrigenEnum.SIU


class NotaCreate(NotaBase):
    """Modelo para crear una nota"""
    pass


class NotaUpdate(BaseModel):
    """Modelo para actualizar una nota"""
    nota: Optional[float] = Field(None, ge=0, le=100)
    tipo_nota: Optional[str] = Field(None, min_length=2, max_length=50)


class Nota(NotaBase):
    """Modelo de nota para respuestas"""
    id_nota: str
    fecha_registro_nota: datetime
    materia: Optional[dict] = None  # Información de la materia
    usuario: Optional[dict] = None  # Información del usuario

    class Config:
        from_attributes = True


# ============= HORARIO =============

class DiaSemanaEnum(str, Enum):
    """Días de la semana"""
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"


class HorarioBase(BaseModel):
    """Modelo base de horario"""
    dia_semana: DiaSemanaEnum
    hora_inicio: str = Field(..., description="Formato HH:MM:SS")
    hora_fin: str = Field(..., description="Formato HH:MM:SS")
    aula: str = Field(..., min_length=1, max_length=50)
    id_grupo: str
    origen: OrigenEnum = OrigenEnum.SIU

    @validator('hora_inicio', 'hora_fin', pre=True)
    def parse_time(cls, v):
        try:
            if isinstance(v, str):
                # Si tiene Z o información de zona horaria, convertir a hora local
                if 'Z' in v or '+' in v:
                    dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                    return dt.strftime('%H:%M:%S')
                # Si ya está en formato HH:MM:SS, validar que sea correcto
                if len(v.split(':')) == 3:
                    datetime.strptime(v, '%H:%M:%S')
                    return v
            raise ValueError()
        except Exception:
            raise ValueError("Formato de hora inválido. Use el formato HH:MM:SS o HH:MM:SS.000Z")

    @validator('hora_fin')
    def validate_time_range(cls, v, values):
        if 'hora_inicio' in values:
            inicio = datetime.strptime(values['hora_inicio'], '%H:%M:%S').time()
            fin = datetime.strptime(v, '%H:%M:%S').time()
            if fin <= inicio:
                raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return v


class HorarioCreate(HorarioBase):
    """Modelo para crear un horario"""
    pass


class HorarioUpdate(BaseModel):
    """Modelo para actualizar un horario"""
    dia_semana: Optional[DiaSemanaEnum] = None
    hora_inicio: Optional[str] = Field(None, description="Formato HH:MM:SS")
    hora_fin: Optional[str] = Field(None, description="Formato HH:MM:SS")
    aula: Optional[str] = Field(None, min_length=1, max_length=50)
    id_grupo: Optional[str] = None
    origen: Optional[OrigenEnum] = None

    @validator('hora_inicio', 'hora_fin', pre=True)
    def parse_time(cls, v):
        if v is None:
            return v
        try:
            if isinstance(v, str):
                # Si tiene Z o información de zona horaria, convertir a hora local
                if 'Z' in v or '+' in v:
                    dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                    return dt.strftime('%H:%M:%S')
                # Si ya está en formato HH:MM:SS, validar que sea correcto
                if len(v.split(':')) == 3:
                    datetime.strptime(v, '%H:%M:%S')
                    return v
            raise ValueError()
        except Exception:
            raise ValueError("Formato de hora inválido. Use el formato HH:MM:SS o HH:MM:SS.000Z")

    @validator('hora_fin')
    def validate_time_range(cls, v, values):
        if v is None:
            return v
        if 'hora_inicio' in values and values['hora_inicio'] is not None:
            inicio = datetime.strptime(values['hora_inicio'], '%H:%M:%S').time()
            fin = datetime.strptime(v, '%H:%M:%S').time()
            if fin <= inicio:
                raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return v


class Horario(BaseModel):
    """Modelo de horario para respuestas"""
    id_horario: str
    dia_semana: DiaSemanaEnum
    hora_inicio: str
    hora_fin: str
    aula: str
    id_grupo: str
    origen: OrigenEnum = OrigenEnum.SIU
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def model_dump(self, *args, **kwargs):
        # Sobrescribir el método model_dump para asegurar que los campos de tiempo sean strings
        data = super().model_dump(*args, **kwargs)
        if isinstance(data.get('hora_inicio'), time):
            data['hora_inicio'] = data['hora_inicio'].strftime('%H:%M:%S')
        if isinstance(data.get('hora_fin'), time):
            data['hora_fin'] = data['hora_fin'].strftime('%H:%M:%S')
        return data


class HorarioUpdate(BaseModel):
    """Modelo para actualizar un horario"""
    dia_semana: Optional[DiaSemanaEnum] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    aula: Optional[str] = Field(None, min_length=1, max_length=50)
    id_grupo: Optional[str] = None


class Horario(HorarioBase):
    """Modelo de horario para respuestas"""
    id_horario: str
    grupo: Optional[dict] = None  # Información del grupo

    class Config:
        from_attributes = True
