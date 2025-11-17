"""
Configuración de la aplicación
Carga variables de entorno y configura parámetros globales
"""
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información del proyecto
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Red Social Universitaria - Universidad del Valle Bolivia")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # Configuración de Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Configuración de seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "red-social-univalle-2025-super-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Configuración de CORS
    CORS_ORIGINS: Optional[str] = '["http://localhost:3000", "http://127.0.0.1:3000"]'
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Configuración de archivos
    UPLOADS_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB en bytes
    
    # Configuración de base de datos
    DATABASE_URL: Optional[str] = None
    
    # Configuración de entorno
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        # Asegurar que la configuración busque el archivo .env dentro de la carpeta `backend`
        # usando una ruta absoluta relativa al paquete `app`. Esto evita problemas cuando
        # Uvicorn se ejecuta desde otra carpeta (ej. la raíz del repo).
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
        case_sensitive = True
        extra = "allow"  # Permite campos extra sin error


# Instancia global de configuración
settings = Settings()
