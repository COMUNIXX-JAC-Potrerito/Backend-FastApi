"""Promueve un usuario existente a superadministrador.

Sirve para crear el PRIMER superadministrador (nadie más puede asignarlo aún).
El usuario debe estar ya registrado (por /api/register).

Uso:
    uv run python crear_superadmin.py correo@ejemplo.com
"""

import sys

from app.db.session import SessionLocal
from app.services.auth.gestion import buscar_por_email
from app.services.auth.roles import ROL_SUPERADMIN


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: uv run python crear_superadmin.py <correo>")
        return 2

    email = sys.argv[1]
    with SessionLocal() as db:
        usuario = buscar_por_email(db, email)
        if usuario is None:
            print(f"No existe un usuario con el correo '{email}'. Regístralo primero.")
            return 1
        usuario.role = ROL_SUPERADMIN
        db.commit()
    print(f"Listo: '{email}' ahora es {ROL_SUPERADMIN}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
