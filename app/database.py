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
        # Intentar usar en orden la KEY de servicio (más permisos), luego la KEY estándar y por último la ANON
        keys_to_try = [
            settings.SUPABASE_SERVICE_KEY,
            settings.SUPABASE_KEY,
            settings.SUPABASE_ANON_KEY,
        ]

        last_exc = None
        for key in keys_to_try:
            if not key:
                continue
            try:
                supabase = create_client(settings.SUPABASE_URL, key)
                logger.info("✅ Conexión a Supabase establecida (key used)")
                last_exc = None
                break
            except Exception as e:
                logger.warning(f"Intento de conexión con una key fallido: {e}")
                last_exc = e

        if supabase is None:
            msg = (
                "No se pudo inicializar el cliente de Supabase. "
                "Verifica que las variables de entorno SUPABASE_URL y SUPABASE_KEY (o SUPABASE_SERVICE_KEY / SUPABASE_ANON_KEY) estén definidas y sean correctas."
            )
            logger.error(f"❌ Error al conectar con Supabase: {last_exc}")
            raise RuntimeError(msg) from last_exc
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
