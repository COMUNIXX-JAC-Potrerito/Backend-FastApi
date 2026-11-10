"""Generación y validación de los JWT de sesión (PyJWT)."""

from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings

ALGORITHM = "HS256"
DURACION_TOKEN = timedelta(hours=8)


def create_access_token(data: dict) -> str:
    """Crea un token firmado que vence en `DURACION_TOKEN`."""
    ahora = datetime.now(UTC)
    contenido = {**data, "iat": ahora, "exp": ahora + DURACION_TOKEN}
    return jwt.encode(contenido, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Devuelve el contenido del token, o None si es inválido, está vencido o no vence."""
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
