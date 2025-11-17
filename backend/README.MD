# Backend - Red Social Universitaria 🎓

API REST desarrollada con FastAPI para la Red Social Universitaria de la Universidad del Valle Bolivia.

## 🚀 Tecnologías

- **FastAPI 0.115.0+** - Framework web moderno y rápido
- **Python 3.11+** - Lenguaje de programación
- **Supabase** - Base de datos PostgreSQL gestionada
- **JWT** - Autenticación con tokens
- **Bcrypt** - Hash de contraseñas
- **Pydantic** - Validación de datos

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de FastAPI
│   ├── config.py            # Configuración de la aplicación
│   ├── database.py          # Conexión a Supabase
│   ├── models/              # Modelos Pydantic
│   │   ├── usuario.py       # Usuario, Estudiante, Docente
│   │   ├── academico.py     # Gestión académica, Materias, Notas
│   │   ├── social.py        # Publicaciones, Comentarios, Reacciones
│   │   ├── mensajeria.py    # Conversaciones y Mensajes
│   │   ├── carpooling.py    # Rutas y Pasajeros
│   │   ├── notificacion.py  # Notificaciones
│   │   └── relacion.py      # Relaciones entre usuarios
│   ├── routes/              # Endpoints/Rutas
│   │   ├── auth.py          # Autenticación (login, registro)
│   │   ├── usuarios.py      # CRUD de usuarios
│   │   ├── estudiantes.py   # Gestión de estudiantes
│   │   ├── docentes.py      # Gestión de docentes
│   │   ├── materias.py      # Gestión de materias
│   │   ├── notas.py         # Consulta de notas
│   │   ├── horarios.py      # Consulta de horarios
│   │   ├── grupos.py        # Gestión de grupos
│   │   ├── publicaciones.py # Red social - Publicaciones
│   │   ├── comentarios.py   # Red social - Comentarios
│   │   ├── reacciones.py    # Red social - Reacciones
│   │   ├── mensajes.py      # Mensajería privada/grupal
│   │   ├── notificaciones.py# Notificaciones
│   │   ├── rutas.py         # Carpooling - Rutas
│   │   └── pasajeros.py     # Carpooling - Pasajeros
│   └── utils/               # Utilidades
│       ├── security.py      # JWT, Hash, Seguridad
│       └── dependencies.py  # Dependencias reutilizables
├── .env                     # Variables de entorno (NO subir a git)
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore
├── requirements.txt         # Dependencias Python
├── baseDeDatos.md          # Esquema de base de datos
├── requerimientos.md       # Requerimientos funcionales
└── README.md
```

## 🔧 Instalación y Configuración

### 1. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env` basado en `.env.example`:

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anonima
SUPABASE_SERVICE_KEY=tu-clave-de-servicio

# Seguridad
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Entorno
ENVIRONMENT=development
DEBUG=True
```

### 4. Ejecutar la aplicación

```bash
# Modo desarrollo (con recarga automática)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Modo producción
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 Endpoints Principales

### 🔐 Autenticación

- `POST /api/v1/auth/register` - Registrar nuevo usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/refresh` - Refrescar token
- `GET /api/v1/auth/me` - Obtener usuario actual

### 👥 Usuarios

- `GET /api/v1/usuarios` - Listar usuarios
- `GET /api/v1/usuarios/{id}` - Obtener usuario
- `PUT /api/v1/usuarios/{id}` - Actualizar usuario
- `DELETE /api/v1/usuarios/{id}` - Eliminar usuario
- `GET /api/v1/usuarios/search/query` - Buscar usuarios

### 🎓 Módulo Académico

- `GET /api/v1/materias/mis-materias` - Mis materias
- `GET /api/v1/notas/mis-notas` - Mis notas
- `GET /api/v1/horarios/mi-horario` - Mi horario
- `GET /api/v1/estudiantes/me` - Mis datos de estudiante

### 📱 Red Social

- `POST /api/v1/publicaciones` - Crear publicación
- `GET /api/v1/publicaciones` - Feed de publicaciones
- `POST /api/v1/comentarios` - Comentar publicación
- `POST /api/v1/reacciones` - Reaccionar a publicación/comentario

### 💬 Mensajería

- `POST /api/v1/mensajes/conversaciones` - Crear conversación
- `GET /api/v1/mensajes/conversaciones` - Mis conversaciones
- `POST /api/v1/mensajes` - Enviar mensaje
- `GET /api/v1/mensajes/conversacion/{id}` - Mensajes de conversación
- `GET /api/v1/mensajes/no-leidos` - Mensajes no leídos

### 🚗 Carpooling

- `POST /api/v1/rutas-carpooling` - Crear ruta
- `GET /api/v1/rutas-carpooling` - Listar rutas disponibles
- `GET /api/v1/rutas-carpooling/mis-rutas` - Mis rutas
- `POST /api/v1/pasajeros` - Postular como pasajero
- `PUT /api/v1/pasajeros/{id}` - Aceptar/rechazar pasajero

### 🔔 Notificaciones

- `GET /api/v1/notificaciones` - Mis notificaciones
- `GET /api/v1/notificaciones/no-leidas` - Notificaciones no leídas
- `PUT /api/v1/notificaciones/{id}/leer` - Marcar como leída

## 🔒 Autenticación y Autorización

La API utiliza **JWT (JSON Web Tokens)** para autenticación:

1. El cliente se registra o inicia sesión
2. El servidor devuelve un `access_token` y `refresh_token`
3. El cliente incluye el token en el header: `Authorization: Bearer <token>`
4. Los endpoints protegidos verifican el token y los permisos

### Roles disponibles:
- **estudiante**: Acceso a módulo académico (consulta), red social, carpooling
- **docente**: Acceso a gestión de notas y materias
- **administrador**: Acceso completo al sistema

## 🗄️ Base de Datos

La base de datos está implementada en **PostgreSQL** a través de **Supabase**. 

Ver esquema completo en: [`baseDeDatos.md`](./baseDeDatos.md)

### Tablas principales:

- **Usuario**: Información básica de usuarios
- **Estudiante**: Datos académicos de estudiantes
- **Docente**: Datos de docentes
- **Materia**: Asignaturas
- **Nota**: Calificaciones
- **Horario**: Horarios de clases
- **Publicacion**: Publicaciones de red social
- **Comentario**: Comentarios en publicaciones
- **Reaccion**: Reacciones (like, love, etc.)
- **Conversacion**: Conversaciones privadas/grupales
- **Mensaje**: Mensajes de chat
- **Ruta**: Rutas de carpooling
- **PasajeroRuta**: Pasajeros en rutas
- **Notificacion**: Notificaciones del sistema

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html
```

## 📝 Notas de Desarrollo

### Convenciones de código:
- Nombres de variables y funciones: `snake_case`
- Nombres de clases: `PascalCase`
- Constantes: `UPPER_CASE`
- Documentación: Docstrings en español

### Buenas prácticas:
- Validación de datos con Pydantic
- Manejo de errores con HTTPException
- Logging de operaciones importantes
- Autenticación JWT en todas las rutas protegidas
- Control de acceso basado en roles

## 🚀 Despliegue

### Variables de entorno de producción:

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<clave-segura-generada-aleatoriamente>
```

### Recomendaciones:
- Usar HTTPS en producción
- Configurar CORS apropiadamente
- Usar variables de entorno seguras
- Implementar rate limiting
- Monitorear logs y errores

## 📄 Licencia

Este proyecto es parte de la Universidad del Valle Bolivia.

## 👥 Equipo de Desarrollo

Red Social Universitaria - Universidad del Valle Bolivia

---

**¿Necesitas ayuda?** Consulta la documentación en `/docs` o contacta al equipo de desarrollo.
│   │   └── usuarios.py
│   └── utils/               # Utilidades
│       ├── security.py      # Hash, JWT, etc.
│       └── dependencies.py  # Dependencias reutilizables
├── .env                     # Variables de entorno (NO subir a git)
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore
├── requirements.txt         # Dependencias del proyecto
└── README.md
```

