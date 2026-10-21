# Generación y validación de tokens JWT para la autenticación del usuario.
from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


# Crea un token de acceso con expiración de 8 horas para uso en la API.
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=8)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


# Verifica el token JWT y devuelve su contenido si es válido y no está vencido.
def decode_access_token(token: str) -> dict | None:
    """Verifica y decodifica un token JWT. Devuelve el payload o None si es
    inválido o está expirado."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
