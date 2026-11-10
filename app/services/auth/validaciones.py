"""Validaciones de correo y contraseña."""

import re

# Formato básico de correo: algo@algo.algo (sin espacios ni segundo @).
_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_LONGITUD_MINIMA_CLAVE = 8


def is_password_strong(password: str) -> bool:
    """Mínimo 8 caracteres, al menos una mayúscula y un número."""
    return (
        len(password) >= _LONGITUD_MINIMA_CLAVE
        and any(c.isupper() for c in password)
        and any(c.isdigit() for c in password)
    )


def is_valid_email(email: str) -> bool:
    return bool(_EMAIL_REGEX.match(email))


def normalizar_email(email: str) -> str:
    """Los correos no distinguen mayúsculas: se comparan y guardan en minúsculas."""
    return email.strip().lower()
