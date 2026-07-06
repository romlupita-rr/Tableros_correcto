from app.db.session import SessionLocal
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.usuario_rol import UsuarioRol
from app.models.rol_permiso import RolPermiso
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.rol_repository import RolRepository


ROLES_SEED = [
    {"rol": "admin", "descripcion": "Acceso total al sistema"},
    {"rol": "consulta", "descripcion": "Solo lectura"},
]

PERMISOS_SEED = [
    {"permiso": "auth.read", "descripcion": "Leer información del usuario autenticado"},
    {"permiso": "usuarios.read", "descripcion": "Consultar usuarios"},
    {"permiso": "usuarios.write", "descripcion": "Crear o modificar usuarios"},
    {"permiso": "usuarios.delete", "descripcion": "Eliminar usuarios"},
]

PERMISOS_POR_ROL = {
    "admin": ["auth.read", "usuarios.read", "usuarios.write", "usuarios.delete"],
    "consulta": ["auth.read", "usuarios.read"],
}

USUARIOS_SEED = [
    {
        "nombre": "Yoselin",
        "a_paterno": "Retama",
        "a_materno": "Cornejo",
        "correo_institucional": "yretama@conalep.edu.mx",
        "username": "yretama@conalep.edu.mx",
        "keycloak_id": None,
        "rol": "admin",
    },
]


def seed():
    db = SessionLocal()

    # 1. Roles
    roles_creados = {}
    for data in ROLES_SEED:
        rol = db.query(Rol).filter_by(rol=data["rol"]).first()
        if not rol:
            rol = Rol(**data)
            db.add(rol)
            db.flush()
            print(f"[Seed] Rol '{rol.rol}' creado.")
        else:
            print(f"[Seed] Rol '{rol.rol}' ya existe, omitido.")
        roles_creados[rol.rol] = rol

    # 2. Permisos
    permisos_creados = {}
    for data in PERMISOS_SEED:
        permiso = db.query(Permiso).filter_by(permiso=data["permiso"]).first()
        if not permiso:
            permiso = Permiso(**data)
            db.add(permiso)
            db.flush()
            print(f"[Seed] Permiso '{permiso.permiso}' creado.")
        else:
            print(f"[Seed] Permiso '{permiso.permiso}' ya existe, omitido.")
        permisos_creados[permiso.permiso] = permiso

    # 3. Asignar permisos a roles
    for rol_nombre, permiso_nombres in PERMISOS_POR_ROL.items():
        rol = roles_creados[rol_nombre]
        for permiso_nombre in permiso_nombres:
            permiso = permisos_creados[permiso_nombre]
            existente = (
                db.query(RolPermiso)
                .filter_by(id_rol=rol.id, id_permiso=permiso.id)
                .first()
            )
            if not existente:
                db.add(RolPermiso(id_rol=rol.id, id_permiso=permiso.id))
                print(f"[Seed] Permiso '{permiso.permiso}' asignado a rol '{rol.rol}'.")

    # 4. Usuarios
    repo_usr = UsuarioRepository(db)
    for data in USUARIOS_SEED:
        rol_nombre = data.pop("rol")
        rol = roles_creados[rol_nombre]

        usuario = repo_usr.get_by_username(data["username"])
        if not usuario:
            usuario = (
                db.query(Usuario)
                .filter(Usuario.correo_institucional == data["correo_institucional"])
                .first()
            )
            if usuario:
                usuario.username = data["username"]
                usuario.keycloak_id = data.get("keycloak_id")
                print(f"[Seed] Usuario existente actualizado a username='{usuario.username}'.")
            else:
                usuario = Usuario(**data)
                db.add(usuario)
                db.flush()
                print(f"[Seed] Usuario '{usuario.username}' creado.")
        else:
            print(f"[Seed] Usuario '{usuario.username}' ya existe, omitido.")

        existente = (
            db.query(UsuarioRol)
            .filter_by(id_usuario=usuario.id, id_rol=rol.id)
            .first()
        )
        if not existente:
            db.add(UsuarioRol(id_usuario=usuario.id, id_rol=rol.id))
            print(f"[Seed] Rol '{rol.rol}' asignado a '{usuario.username}'.")
        else:
            print(f"[Seed] '{usuario.username}' ya tiene el rol '{rol.rol}', omitido.")

    db.commit()
    db.close()
    print("[Seed] Completado.")


if __name__ == "__main__":
    seed()
