"""
Modelos Pydantic para Usuario, Estudiante, Docente y Administrador
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class RolEnum(str, Enum):
    """Roles disponibles en el sistema"""
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente"
    ADMINISTRADOR = "administrador"


class UsuarioBase(BaseModel):
    """Modelo base de usuario"""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr = Field(..., max_length=150)
    rol: RolEnum


class UsuarioCreate(UsuarioBase):
    """Modelo para crear un usuario"""
    contrasena: str = Field(..., min_length=8, max_length=100)
    
    @validator('contrasena')
    def validate_password(cls, v):
        """Validar que la contraseña tenga al menos una mayúscula, minúscula y número"""
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


class UsuarioUpdate(BaseModel):
    """Modelo para actualizar un usuario"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    correo: Optional[EmailStr] = Field(None, max_length=150)
    contrasena: Optional[str] = Field(None, min_length=8, max_length=100)
    foto_perfil: Optional[str] = Field(None, max_length=500)
    activo: Optional[bool] = None


class UsuarioInDB(UsuarioBase):
    """Modelo de usuario en base de datos"""
    id_user: str
    contrasena: str  # Hash de la contraseña
    fecha_registro: datetime
    activo: bool = True
    foto_perfil: Optional[str] = None

    class Config:
        from_attributes = True


class Usuario(UsuarioBase):
    """Modelo de usuario para respuestas (sin contraseña)"""
    id_user: str
    fecha_registro: datetime
    activo: bool = True
    foto_perfil: Optional[str] = None

    class Config:
        from_attributes = True


# ============= ESTUDIANTE =============

class EstudianteBase(BaseModel):
    """Modelo base de estudiante"""
    carrera: str = Field(..., min_length=3, max_length=150)
    semestre: int = Field(..., ge=1, le=12)
    id_grupo: Optional[str] = None


class EstudianteCreate(EstudianteBase):
    """Modelo para crear un estudiante"""
    ci_est: str = Field(..., min_length=5, max_length=20)
    # Datos del usuario
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr = Field(..., max_length=150)
    contrasena: str = Field(..., min_length=8, max_length=100)


class EstudianteUpdate(BaseModel):
    """Modelo para actualizar un estudiante"""
    carrera: Optional[str] = Field(None, min_length=3, max_length=150)
    semestre: Optional[int] = Field(None, ge=1, le=12)
    id_grupo: Optional[str] = None


class EstudianteInDB(EstudianteBase):
    """Modelo de estudiante en base de datos"""
    ci_est: str
    id_user: str

    class Config:
        from_attributes = True


class Estudiante(EstudianteBase):
    """Modelo de estudiante para respuestas"""
    ci_est: str
    id_user: str
    usuario: Optional[Usuario] = None

    class Config:
        from_attributes = True


# ============= DOCENTE =============

class DocenteBase(BaseModel):
    """Modelo base de docente"""
    especialidad_doc: str = Field(..., min_length=3, max_length=150)


class DocenteCreate(DocenteBase):
    """Modelo para crear un docente"""
    ci_doc: str = Field(..., min_length=5, max_length=20)
    # Datos del usuario
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr = Field(..., max_length=150)
    contrasena: str = Field(..., min_length=8, max_length=100)


class DocenteUpdate(BaseModel):
    """Modelo para actualizar un docente"""
    especialidad_doc: Optional[str] = Field(None, min_length=3, max_length=150)


class DocenteInDB(DocenteBase):
    """Modelo de docente en base de datos"""
    ci_doc: str
    id_user: str

    class Config:
        from_attributes = True


class Docente(BaseModel):
    """Modelo de docente para respuestas"""
    ci_doc: str
    id_user: str
    especialidad_doc: str = Field(..., min_length=3, max_length=150)
    usuario: dict

    class Config:
        from_attributes = True


# ============= ADMINISTRADOR =============

class AdministradorCreate(BaseModel):
    """Modelo para crear un administrador"""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    correo: EmailStr = Field(..., max_length=150)
    contrasena: str = Field(..., min_length=8, max_length=100)


class Administrador(BaseModel):
    """Modelo de administrador para respuestas"""
    id_user: str
    usuario: Usuario

    class Config:
        from_attributes = True
