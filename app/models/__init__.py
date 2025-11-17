"""
Modelos de datos de la aplicación
"""
from app.models.usuario import Usuario, Estudiante, Docente, Administrador
from app.models.academico import (
    GestionAcademica,
    Grupo,
    Materia,
    GrupoMateria,
    Nota,
    Horario
)
from app.models.social import (
    Publicacion,
    Media,
    Comentario,
    Reaccion
)
from app.models.mensajeria import (
    Conversacion,
    UsuarioConversacion,
    Mensaje
)
from app.models.carpooling import (
    Ruta,
    Parada,
    PasajeroRuta
)
from app.models.notificacion import Notificacion
from app.models.relacion import RelacionUsuario

__all__ = [
    # Usuarios
    "Usuario",
    "Estudiante",
    "Docente",
    "Administrador",
    # Académico
    "GestionAcademica",
    "Grupo",
    "Materia",
    "GrupoMateria",
    "Nota",
    "Horario",
    # Social
    "Publicacion",
    "Media",
    "Comentario",
    "Reaccion",
    # Mensajería
    "Conversacion",
    "UsuarioConversacion",
    "Mensaje",
    # Carpooling
    "Ruta",
    "Parada",
    "PasajeroRuta",
    # Otros
    "Notificacion",
    "RelacionUsuario",
]
