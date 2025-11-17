-- 1. TABLA USUARIO
CREATE TABLE Usuario (
    id_user VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('estudiante', 'docente', 'administrador')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true
);

ALTER TABLE Usuario ADD COLUMN foto_perfil VARCHAR(500);

-- 2. TABLA GESTION_ACADEMICA
CREATE TABLE GestionAcademica (
    id_gestion VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre_gestion VARCHAR(50) NOT NULL UNIQUE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'finalizado')),
    CHECK (fecha_fin > fecha_inicio)
);


-- 3. TABLA GRUPO
CREATE TABLE Grupo (
    id_grupo VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre_grupo VARCHAR(100) NOT NULL,
    gestion_grupo VARCHAR(36) NOT NULL REFERENCES GestionAcademica(id_gestion) ON DELETE RESTRICT,
    UNIQUE(nombre_grupo, gestion_grupo)
);


-- 4. TABLA ESTUDIANTE
CREATE TABLE Estudiante (
    ci_est VARCHAR(20) PRIMARY KEY,
    id_user VARCHAR(36) UNIQUE NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    carrera VARCHAR(150) NOT NULL,
    semestre INTEGER NOT NULL CHECK (semestre >= 1 AND semestre <= 12),
    id_grupo VARCHAR(36) REFERENCES Grupo(id_grupo) ON DELETE SET NULL
);

-- 5. TABLA DOCENTE
CREATE TABLE Docente (
    ci_doc VARCHAR(20) PRIMARY KEY,
    id_user VARCHAR(36) UNIQUE NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    especialidad_doc VARCHAR(150) NOT NULL
);

-- 6. TABLA MATERIA
CREATE TABLE Materia (
    id_materia VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre_materia VARCHAR(150) NOT NULL,
    codigo_materia VARCHAR(20) UNIQUE NOT NULL,
    id_doc VARCHAR(20) REFERENCES Docente(ci_doc) ON DELETE SET NULL,
    origen VARCHAR(10) DEFAULT 'SIU' CHECK (origen IN ('SIU', 'MANUAL'))
);


-- 7. TABLA GRUPOMATERIA
CREATE TABLE GrupoMateria (
    id_grupo_materia VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    id_grupo VARCHAR(36) NOT NULL REFERENCES Grupo(id_grupo) ON DELETE CASCADE,
    id_materia VARCHAR(36) NOT NULL REFERENCES Materia(id_materia) ON DELETE CASCADE,
    origen VARCHAR(10) DEFAULT 'SIU' CHECK (origen IN ('SIU', 'MANUAL')),
    UNIQUE(id_grupo, id_materia)
);

-- 8. TABLA NOTA
CREATE TABLE Nota (
    id_nota VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nota DECIMAL(5,2) NOT NULL CHECK (nota >= 0 AND nota <= 100),
    tipo_nota VARCHAR(50) NOT NULL,
    fecha_registro_nota TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    id_materia VARCHAR(36) NOT NULL REFERENCES Materia(id_materia) ON DELETE CASCADE,
    origen VARCHAR(10) DEFAULT 'SIU' CHECK (origen IN ('SIU', 'MANUAL'))
);


-- 9. TABLA HORARIO
CREATE TABLE Horario (
    id_horario VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    dia_semana VARCHAR(15) NOT NULL CHECK (dia_semana IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado')),
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    aula VARCHAR(50) NOT NULL,
    id_grupo VARCHAR(36) NOT NULL REFERENCES Grupo(id_grupo) ON DELETE CASCADE,
    origen VARCHAR(10) DEFAULT 'SIU' CHECK (origen IN ('SIU', 'MANUAL')),
    CHECK (hora_fin > hora_inicio)
);


-- 10. TABLA RUTA (Carpooling)
CREATE TABLE Ruta (
    id_ruta VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    punto_inicio VARCHAR(200) NOT NULL,
    punto_destino VARCHAR(200) NOT NULL,
    hora_salida TIME NOT NULL,
    dias_disponibles VARCHAR(100) NOT NULL,
    capacidad_ruta INTEGER NOT NULL CHECK (capacidad_ruta > 0 AND capacidad_ruta <= 8),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    activa BOOLEAN DEFAULT true
);

-- 11. TABLA PARADA
CREATE TABLE Parada (
    id_parada VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    orden_parada INTEGER NOT NULL CHECK (orden_parada > 0),
    ubicacion_parada VARCHAR(200) NOT NULL,
    id_ruta VARCHAR(36) NOT NULL REFERENCES Ruta(id_ruta) ON DELETE CASCADE,
    UNIQUE(id_ruta, orden_parada)
);


-- 12. TABLA PASAJERO_RUTA
CREATE TABLE PasajeroRuta (
    id_pasajero_ruta VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aceptado', 'rechazado', 'cancelado')),
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    id_ruta VARCHAR(36) NOT NULL REFERENCES Ruta(id_ruta) ON DELETE CASCADE,
    UNIQUE(id_user, id_ruta)
);


-- 13. TABLA PUBLICACION (Red Social)
CREATE TABLE Publicacion (
    id_publicacion VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    contenido TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('texto', 'imagen', 'documento', 'enlace', 'ruta_carpooling')),
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE
);

-- 14. TABLA MEDIA
CREATE TABLE Media (
    id_media VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('imagen', 'video', 'documento', 'audio')),
    url VARCHAR(500) NOT NULL,
    id_publicacion VARCHAR(36) NOT NULL REFERENCES Publicacion(id_publicacion) ON DELETE CASCADE
);


-- 15. TABLA COMENTARIO
CREATE TABLE Comentario (
    id_comentario VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    contenido TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    id_publicacion VARCHAR(36) NOT NULL REFERENCES Publicacion(id_publicacion) ON DELETE CASCADE
);



-- 16. TABLA REACCION
CREATE TABLE Reaccion (
    id_reaccion VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    tipo_reac VARCHAR(20) NOT NULL CHECK (tipo_reac IN ('like', 'dislike', 'love', 'wow', 'sad', 'angry')),
    fecha_creacion_reac TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    id_publicacion VARCHAR(36) REFERENCES Publicacion(id_publicacion) ON DELETE CASCADE,
    id_comentario VARCHAR(36) REFERENCES Comentario(id_comentario) ON DELETE CASCADE,
    CHECK (
        (id_publicacion IS NOT NULL AND id_comentario IS NULL) OR
        (id_publicacion IS NULL AND id_comentario IS NOT NULL)
    ),
    UNIQUE(id_user, id_publicacion, tipo_reac),
    UNIQUE(id_user, id_comentario, tipo_reac)
);


-- 17. TABLA CONVERSACION (Mensajería)
CREATE TABLE Conversacion (
    id_conversacion VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('privada', 'grupal')),
    nombre VARCHAR(150),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 18. TABLA USUARIO_CONVERSACION
CREATE TABLE UsuarioConversacion (
    id_usuario_conversacion VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    id_usuario VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    id_conversacion VARCHAR(36) NOT NULL REFERENCES Conversacion(id_conversacion) ON DELETE CASCADE,
    rol VARCHAR(20) DEFAULT 'miembro' CHECK (rol IN ('admin', 'miembro')),
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_usuario, id_conversacion)
);


-- 19. TABLA MENSAJE
CREATE TABLE Mensaje (
    id_mensaje VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    contenido TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leido BOOLEAN DEFAULT false,
    id_conversacion VARCHAR(36) NOT NULL REFERENCES Conversacion(id_conversacion) ON DELETE CASCADE,
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE
);

-- 20. TABLA NOTIFICACION
CREATE TABLE Notificacion (
    id_notificacion VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    contenido TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leida BOOLEAN DEFAULT false,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('comentario', 'reaccion', 'solicitud_amistad', 'solicitud_ruta', 'mensaje', 'nota_nueva', 'otro')),
    id_user VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE
);


-- 21. TABLA RELACION_USUARIO (Amistades)
CREATE TABLE RelacionUsuario (
    id_relacion_usuario VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    id_usuario1 VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    id_usuario2 VARCHAR(36) NOT NULL REFERENCES Usuario(id_user) ON DELETE CASCADE,
    tipo VARCHAR(20) DEFAULT 'amistad' CHECK (tipo IN ('amistad', 'bloqueado')),
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'aceptado', 'rechazado')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta TIMESTAMP,
    CHECK (id_usuario1 != id_usuario2),
    UNIQUE(id_usuario1, id_usuario2)
);




CREATE INDEX idx_usuario_correo ON Usuario(correo);
CREATE INDEX idx_usuario_rol ON Usuario(rol);
CREATE INDEX idx_estudiante_user ON Estudiante(id_user);
CREATE INDEX idx_estudiante_grupo ON Estudiante(id_grupo);
CREATE INDEX idx_docente_user ON Docente(id_user);
CREATE INDEX idx_materia_docente ON Materia(id_doc);
CREATE INDEX idx_nota_user ON Nota(id_user);
CREATE INDEX idx_nota_materia ON Nota(id_materia);
CREATE INDEX idx_horario_grupo ON Horario(id_grupo);
CREATE INDEX idx_publicacion_user ON Publicacion(id_user);
CREATE INDEX idx_publicacion_fecha ON Publicacion(fecha_creacion DESC);
CREATE INDEX idx_comentario_publicacion ON Comentario(id_publicacion);
CREATE INDEX idx_comentario_user ON Comentario(id_user);
CREATE INDEX idx_mensaje_conversacion ON Mensaje(id_conversacion);
CREATE INDEX idx_mensaje_leido ON Mensaje(leido, fecha_envio);
CREATE INDEX idx_notificacion_user ON Notificacion(id_user, leida);
CREATE INDEX idx_pasajero_ruta ON PasajeroRuta(id_ruta, estado);
CREATE INDEX idx_ruta_activa ON Ruta(activa, fecha_creacion);****




-------------------------------------------------------------------------------------------------




