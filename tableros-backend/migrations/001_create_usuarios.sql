-- Migración 001: Crear tabla de usuarios del sistema
-- Ejecutar una sola vez en la BD

CREATE TABLE IF NOT EXISTS usuarios (
    id                    SERIAL PRIMARY KEY,
    nombre                VARCHAR(100) NOT NULL,
    a_paterno             VARCHAR(100) NOT NULL,
    a_materno             VARCHAR(100),
    correo_institucional  VARCHAR(255) NOT NULL UNIQUE,
    username              VARCHAR(150) NOT NULL UNIQUE,
    keycloak_id           VARCHAR(255) UNIQUE,
    estado                BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_modificacion    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_eliminacion     TIMESTAMP WITH TIME ZONE
);

-- Trigger para actualizar fecha_modificacion automáticamente
CREATE OR REPLACE FUNCTION update_fecha_modificacion_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_usuarios_fecha_modificacion
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion_column();
