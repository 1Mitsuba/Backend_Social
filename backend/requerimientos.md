Requerimientos Funcionales 
1. Gestión de usuarios (estudiantes y docentes)
•	RF1: El sistema debe permitir el registro e inicio de sesión de usuarios (estudiantes y docentes) con credenciales institucionales.
•	RF2: El sistema debe permitir que los usuarios gestionen sus datos básicos de perfil (nombre, correo y contraseña).
•	RF3: El sistema debe permitir a los estudiantes gestionar sus datos académicos (carrera, semestre y grupo).
•	RF4: El sistema debe permitir a los docentes gestionar sus datos académicos (especialidad).
2. Módulo Académico (solo consulta para estudiantes)
•	RF5: El estudiante podrá consultar las materias en las que está inscrito.
•	RF6: El estudiante podrá consultar su horario semanal.
•	RF7: El estudiante podrá consultar sus notas parciales y finales en cada materia, las cuales serán cargadas previamente desde la base de datos institucional.
•	RF8: El estudiante podrá consultar la información de los docentes de sus materias (nombre, correo y especialidad).
3. Red Social UniversitariaRF9: El sistema debe permitir a los usuarios crear publicaciones (texto, enlaces o rutas de carpooling).
•	RF9: El sistema debe permitir a los usuarios crear publicaciones (texto, imágenes, documentos, enlaces o rutas de carpooling).
•	RF10: El sistema debe permitir a los usuarios comentar publicaciones de otros.
•	RF11: El sistema debe permitir a los usuarios reaccionar a publicaciones y comentarios (like, dislike, etc.).
•	RF12: El sistema debe permitir a los usuarios recibir notificaciones sobre interacciones (comentarios, reacciones, solicitudes de amistad, invitaciones a rutas).
•	RF13: El sistema debe permitir a los usuarios enviar y recibir mensajes privados o grupales.
4. Módulo de Carpooling Universitario
•	RF14: Un estudiante podrá crear una ruta indicando punto de inicio, destino, hora de salida, días disponibles y capacidad.
•	RF15: El sistema debe permitir registrar paradas intermedias en una ruta.
•	RF16: Un estudiante podrá postularse como pasajero en una ruta creada por otro estudiante.
•	RF17: El creador de la ruta (conductor) podrá aceptar o rechazar pasajeros.
•	RF18: El sistema debe mostrar la lista de pasajeros aceptados en cada ruta.
Requerimientos No Funcionales
1. Plataforma y tecnología
•	RNF1: El sistema tendrá dos clientes:
o	Una aplicación web desarrollada en React Native Web.
o	Una aplicación móvil desarrollada en Android Studio (Java/Kotlin).
•	RNF2: El backend será desarrollado en FastAPI (Python).
•	RNF3: La base de datos será PostgreSQL en Supabase (en la nube).
2. Rendimiento
•	RNF4: El sistema debe permitir hasta 500 usuarios concurrentes en la fase inicial.
•	RNF5: Las consultas de notas, publicaciones y rutas deben responder en menos de 3 segundos.
3. Seguridad
•	RNF6: Las contraseñas de los usuarios deben almacenarse de forma segura (hash + salt).
•	RNF7: La comunicación entre cliente y servidor debe estar protegida con HTTPS y JWT para autenticación.
•	RNF8: El sistema debe implementar control de roles y permisos (estudiante, docente y administrador).
4. Usabilidad
•	RNF9: La interfaz debe ser intuitiva y responsiva, optimizada para dispositivos móviles.
•	RNF10: La aplicación debe estar disponible en idioma español.
•	RNF11: La aplicación debe contar con diseño accesible siguiendo buenas prácticas (contraste, tamaños de letra, compatibilidad con lectores de pantalla).
