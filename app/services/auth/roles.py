"""Roles de usuario del sistema y qué puede hacer cada uno.

Los 4 roles definidos en el proyecto: usuario, administrador,
superadministrador y entidad.
"""

ROL_USUARIO = "usuario"
ROL_ADMIN = "administrador"
ROL_SUPERADMIN = "superadministrador"
ROL_ENTIDAD = "entidad"

ROLES_VALIDOS = [ROL_USUARIO, ROL_ADMIN, ROL_SUPERADMIN, ROL_ENTIDAD]

# Roles que pueden gestionar PQRS (ver entrantes, asignar comité, cambiar estado, historial)
ROLES_GESTION = [ROL_ADMIN, ROL_SUPERADMIN]


def es_rol_valido(rol: str) -> bool:
    return rol in ROLES_VALIDOS
