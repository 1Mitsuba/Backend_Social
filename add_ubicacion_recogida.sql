-- Agregar columna ubicacion_recogida a la tabla pasajeroruta
ALTER TABLE pasajeroruta 
ADD COLUMN IF NOT EXISTS ubicacion_recogida VARCHAR(200);

-- Agregar comentario a la columna
COMMENT ON COLUMN pasajeroruta.ubicacion_recogida IS 'Ubicación donde el pasajero será recogido';
