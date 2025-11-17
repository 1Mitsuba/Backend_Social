"""
Punto de entrada principal de la aplicación FastAPI
Red Social Universitaria - Universidad del Valle Bolivia
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import init_db

# Importar routers
from app.routes import auth, usuarios, estudiantes, docentes
from app.routes import materias, notas, horarios, grupos
from app.routes import publicaciones, comentarios, reacciones
from app.routes import mensajes, notificaciones
from app.routes import rutas, pasajeros

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejo del ciclo de vida de la aplicación
    """
    # Startup
    logger.info("🚀 Iniciando aplicación...")
    try:
        init_db()
        logger.info("✅ Base de datos inicializada")
    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 Cerrando aplicación...")


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API REST para la Red Social Universitaria de la Universidad del Valle Bolivia",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para registrar todas las peticiones
    """
    start_time = time.time()
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Manejador de errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador personalizado para errores de validación
    """
    # Convertir errores a formato serializable
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": list(error.get("loc", [])),
            "msg": str(error.get("msg", "")),
            "type": str(error.get("type", ""))
        }
        # Solo agregar 'ctx' si existe y es serializable
        if "ctx" in error and error["ctx"]:
            try:
                error_dict["ctx"] = {k: str(v) for k, v in error["ctx"].items()}
            except:
                pass
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "message": "Error de validación en los datos enviados"
        }
    )


# Manejador de errores genéricos
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejador para excepciones no controladas
    """
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Error interno del servidor",
            "message": str(exc) if settings.DEBUG else "Ha ocurrido un error"
        }
    )


# Rutas principales
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz - Información de la API
    """
    return {
        "message": "Red Social Universitaria - Universidad del Valle Bolivia",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de verificación de salud
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Incluir routers con prefijo API v1
api_prefix = settings.API_V1_STR

# Autenticación
app.include_router(auth.router, prefix=api_prefix, tags=["Autenticación"])

# Gestión de usuarios
app.include_router(usuarios.router, prefix=api_prefix, tags=["Usuarios"])
app.include_router(estudiantes.router, prefix=api_prefix, tags=["Estudiantes"])
app.include_router(docentes.router, prefix=api_prefix, tags=["Docentes"])

# Módulo académico
app.include_router(materias.router, prefix=api_prefix, tags=["Materias"])
app.include_router(notas.router, prefix=api_prefix, tags=["Notas"])
app.include_router(horarios.router, prefix=api_prefix, tags=["Horarios"])
app.include_router(grupos.router, prefix=api_prefix, tags=["Grupos"])

# Red social
app.include_router(publicaciones.router, prefix=api_prefix, tags=["Publicaciones"])
app.include_router(comentarios.router, prefix=api_prefix, tags=["Comentarios"])
app.include_router(reacciones.router, prefix=api_prefix, tags=["Reacciones"])

# Mensajería
app.include_router(mensajes.router, prefix=api_prefix, tags=["Mensajes"])
app.include_router(notificaciones.router, prefix=api_prefix, tags=["Notificaciones"])

# Carpooling
app.include_router(rutas.router, prefix=api_prefix, tags=["Rutas Carpooling"])
app.include_router(pasajeros.router, prefix=api_prefix, tags=["Pasajeros"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
