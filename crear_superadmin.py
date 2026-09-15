"""Promueve un usuario existente a superadministrador.

Sirve para crear el PRIMER superadministrador (nadie más puede asignarlo aún).
El usuario debe estar ya registrado (por /api/register).

Uso:
    uv run python crear_superadmin.py correo@ejemplo.com
"""

import sys

from app.db.session import SessionLocal
from app.models.user import User
from app.services.auth.roles import ROL_SUPERADMIN


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: uv run python crear_superadmin.py <correo>")
        return

    email = sys.argv[1]
    db = SessionLocal()
    try:
        usuario = db.query(User).filter(User.email == email).first()
        if usuario is None:
            print(f"No existe un usuario con el correo '{email}'. Regístralo primero.")
            return

        usuario.role = ROL_SUPERADMIN
        db.commit()
        print(f"Listo: '{email}' ahora es {ROL_SUPERADMIN}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
