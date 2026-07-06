-- Migración 002: Crear tablas de roles, permisos y relaciones
-- Ejecutar una sola vez en la BD

CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL PRIMARY KEY,
    rol         VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS permisos (
    id          SERIAL PRIMARY KEY,
    permiso     VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS usuarios_roles (
    id_usuario  INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    id_rol      INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (id_usuario, id_rol)
);

CREATE TABLE IF NOT EXISTS roles_permisos (
    id_rol      INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    id_permiso  INTEGER NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (id_rol, id_permiso)
);

-- Datos semilla: permisos base del sistema
INSERT INTO permisos (permiso, descripcion) VALUES
    ('auth.read',     'Leer información del usuario autenticado'),
    ('usuarios.read',    'Consultar usuarios'),
    ('usuarios.write',   'Crear o modificar usuarios'),
    ('usuarios.delete',  'Eliminar usuarios')
ON CONFLICT (permiso) DO NOTHING;

-- Datos semilla: roles base
INSERT INTO roles (rol, descripcion) VALUES
    ('admin',    'Acceso total al sistema'),
    ('consulta', 'Solo lectura')
ON CONFLICT (rol) DO NOTHING;

-- Asignar permisos al rol admin
INSERT INTO roles_permisos (id_rol, id_permiso)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.rol = 'admin'
  AND p.permiso IN ('auth.read', 'usuarios.read', 'usuarios.write', 'usuarios.delete')
ON CONFLICT DO NOTHING;

-- Asignar permisos al rol consulta
INSERT INTO roles_permisos (id_rol, id_permiso)
SELECT r.id, p.id
FROM roles r, permisos p
WHERE r.rol = 'consulta'
  AND p.permiso IN ('auth.read', 'usuarios.read')
ON CONFLICT DO NOTHING;
