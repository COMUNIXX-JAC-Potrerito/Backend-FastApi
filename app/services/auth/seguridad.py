"""Cifrado y verificación de contraseñas con bcrypt.

Se usa la librería `bcrypt` directamente (passlib ya no se mantiene). Los hashes
`$2b$` creados antes con passlib son compatibles y siguen verificando.
"""

import bcrypt

# bcrypt solo procesa los primeros 72 bytes; los esquemas ya rechazan claves más largas.
_MAX_BYTES = 72


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:_MAX_BYTES], bcrypt.gensalt()).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """True si la clave corresponde al hash; un hash corrupto cuenta como no válido."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:_MAX_BYTES], hashed_password.encode("ascii"))
    except ValueError, UnicodeEncodeError:
        return False
