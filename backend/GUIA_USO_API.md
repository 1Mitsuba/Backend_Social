# 🎉 ¡Backend Funcionando Correctamente!

## ✅ Estado Actual

### Servidor
- **Estado**: ✅ FUNCIONANDO
- **URL**: http://127.0.0.1:8000
- **Documentación**: http://127.0.0.1:8000/docs
- **Puerto**: 8000

### Base de Datos Supabase
- **Estado**: ✅ CONECTADO
- **Tablas**: 21 tablas creadas
- **Proyecto**: embbopesdstaivgnecpe

---

## 🚀 Probar el Backend

### 1. Documentación Interactiva (Swagger)
Abre en tu navegador:
```
http://127.0.0.1:8000/docs
```

### 2. Probar Registro de Usuario

#### Opción A: Desde PowerShell
```powershell
$body = @{
    nombre = "Juan"
    apellido = "Pérez"
    correo = "juan.perez@example.com"
    rol = "estudiante"
    contrasena = "MiPassword123"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/auth/register" `
  -ContentType "application/json" `
  -Body $body
```

#### Opción B: Desde el navegador (Swagger UI)
1. Ve a: http://127.0.0.1:8000/docs
2. Busca **POST /api/v1/auth/register**
3. Haz clic en **"Try it out"**
4. Rellena los datos:
```json
{
  "nombre": "María",
  "apellido": "García",
  "correo": "maria@example.com",
  "rol": "estudiante",
  "contrasena": "MiPassword456"
}
```
5. Haz clic en **"Execute"**

### 3. Iniciar Sesión

Una vez registrado, prueba el login:

```powershell
# Login
$loginBody = @{
    username = "maria@example.com"
    password = "MiPassword456"
} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
  -ContentType "application/x-www-form-urlencoded" `
  -Body "username=maria@example.com&password=MiPassword456"

# El token estará en $response.access_token
Write-Host "Token: $($response.access_token)"
```

### 4. Usar Endpoints Protegidos

Con el token que obtienes del login, puedes acceder a los demás endpoints:

```powershell
# Obtener información del usuario actual
$token = "tu_access_token_aqui"

Invoke-RestMethod -Method Get `
  -Uri "http://127.0.0.1:8000/api/v1/auth/me" `
  -Headers @{ Authorization = "Bearer $token" }
```

---

## 📊 Endpoints Disponibles

### 🔓 Públicos (sin autenticación)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar nuevo usuario |
| POST | `/api/v1/auth/login` | Iniciar sesión |
| POST | `/api/v1/auth/refresh` | Refrescar token |

### 🔒 Protegidos (requieren token)

#### Usuarios
- GET `/api/v1/usuarios` - Listar usuarios
- GET `/api/v1/usuarios/{id}` - Obtener usuario
- PUT `/api/v1/usuarios/{id}` - Actualizar usuario
- DELETE `/api/v1/usuarios/{id}` - Eliminar usuario

#### Estudiantes
- GET `/api/v1/estudiantes` - Listar estudiantes
- GET `/api/v1/estudiantes/{ci}` - Obtener estudiante
- POST `/api/v1/estudiantes` - Crear estudiante
- PUT `/api/v1/estudiantes/{ci}` - Actualizar estudiante
- DELETE `/api/v1/estudiantes/{ci}` - Eliminar estudiante

#### Red Social
- GET `/api/v1/publicaciones` - Feed de publicaciones
- POST `/api/v1/publicaciones` - Crear publicación
- GET `/api/v1/publicaciones/{id}` - Ver publicación
- PUT `/api/v1/publicaciones/{id}` - Editar publicación
- DELETE `/api/v1/publicaciones/{id}` - Eliminar publicación

#### Comentarios
- GET `/api/v1/comentarios/publicacion/{id}` - Comentarios de una publicación
- POST `/api/v1/comentarios` - Crear comentario
- PUT `/api/v1/comentarios/{id}` - Editar comentario
- DELETE `/api/v1/comentarios/{id}` - Eliminar comentario

#### Reacciones
- POST `/api/v1/reacciones` - Reaccionar
- GET `/api/v1/reacciones/publicacion/{id}` - Reacciones de publicación
- DELETE `/api/v1/reacciones/{id}` - Eliminar reacción

#### Mensajería
- GET `/api/v1/mensajes/conversaciones` - Mis conversaciones
- POST `/api/v1/mensajes/conversacion` - Crear conversación
- GET `/api/v1/mensajes/conversacion/{id}` - Mensajes de conversación
- POST `/api/v1/mensajes` - Enviar mensaje
- PUT `/api/v1/mensajes/{id}/leer` - Marcar como leído

#### Carpooling
- GET `/api/v1/rutas` - Listar rutas
- POST `/api/v1/rutas` - Crear ruta
- GET `/api/v1/rutas/{id}` - Ver ruta
- PUT `/api/v1/rutas/{id}` - Actualizar ruta
- DELETE `/api/v1/rutas/{id}` - Cancelar ruta
- POST `/api/v1/rutas/{id}/paradas` - Agregar parada

#### Módulo Académico
- GET `/api/v1/materias` - Listar materias
- GET `/api/v1/notas/estudiante/{ci}` - Notas de estudiante
- GET `/api/v1/horarios/grupo/{id}` - Horario de grupo
- GET `/api/v1/grupos` - Listar grupos

---

## 🎯 Flujo Típico de Uso

### 1. Registro
```
POST /api/v1/auth/register
```

### 2. Login
```
POST /api/v1/auth/login
→ Recibe access_token
```

### 3. Usar API
```
GET /api/v1/publicaciones
Headers: Authorization: Bearer {access_token}
```

### 4. Crear Contenido
```
POST /api/v1/publicaciones
Headers: Authorization: Bearer {access_token}
Body: { contenido: "Mi primera publicación!" }
```

---

## 🔍 Health Check

Verificar que el servidor esté funcionando:
```
GET http://127.0.0.1:8000/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 📱 Próximos Pasos

1. ✅ **Probar el registro** en http://127.0.0.1:8000/docs
2. ✅ **Hacer login** y guardar el token
3. ✅ **Probar crear una publicación**
4. ✅ **Probar crear una ruta de carpooling**
5. ✅ **Conectar el frontend** con el backend

---

## 🆘 Solución de Problemas

### El servidor no inicia
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Error de conexión a Supabase
Verificar `.env`:
- SUPABASE_URL debe coincidir con tu proyecto
- SUPABASE_KEY debe ser válido

### Token expirado
Hacer login nuevamente para obtener un nuevo token

---

**¡Todo listo para usar!** 🚀

La API está completamente funcional y lista para conectar con tu frontend React.
