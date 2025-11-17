"""
Configuración de la base de datos con Supabase
"""
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Cliente de Supabase
supabase: Client = None


def get_supabase_client() -> Client:
    """
    Obtiene o crea el cliente de Supabase
    """
    global supabase
    if supabase is None:
        try:
            supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("✅ Conexión a Supabase establecida")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {e}")
            raise
    return supabase


def init_db():
    """
    Inicializa la conexión a la base de datos
    """
    try:
        get_supabase_client()
        logger.info("✅ Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar la base de datos: {e}")
        raise


# Dependencia para obtener el cliente de Supabase en las rutas
async def get_db() -> Client:
    """
    Dependencia para inyectar el cliente de Supabase en las rutas
    """
    return get_supabase_client()
