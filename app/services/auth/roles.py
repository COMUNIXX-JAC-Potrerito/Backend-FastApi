"""Roles de usuario del sistema y qué puede hacer cada uno."""

ROL_USUARIO = "usuario"
ROL_ADMIN = "administrador"
ROL_SUPERADMIN = "superadministrador"
ROL_ENTIDAD = "entidad"

ROLES_VALIDOS = (ROL_USUARIO, ROL_ADMIN, ROL_SUPERADMIN, ROL_ENTIDAD)

# Dignatarios: gestionan PQRS, publicaciones, mensajes internos, encuestas, etc.
ROLES_GESTION = (ROL_ADMIN, ROL_SUPERADMIN)


def es_rol_valido(rol: str) -> bool:
    """Indica si el rol está entre los válidos."""
    return rol in ROLES_VALIDOS


def es_dignatario(rol: str | None) -> bool:
    """Indica si el rol permite gestionar (administrador o superadministrador)."""
    return rol in ROLES_GESTION
