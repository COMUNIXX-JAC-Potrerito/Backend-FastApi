"""Generación y validación de los JWT de sesión."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"
DURACION_TOKEN = timedelta(hours=8)


def create_access_token(data: dict) -> str:
    """Crea un token firmado que vence en `DURACION_TOKEN`."""
    contenido = {**data, "exp": datetime.now(UTC) + DURACION_TOKEN}
    return jwt.encode(contenido, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Devuelve el contenido del token, o None si es inválido o está vencido."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
