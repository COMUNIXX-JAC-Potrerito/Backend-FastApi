from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth.tokens import decode_access_token

# Lee el token del header "Authorization: Bearer <token>".
# tokenUrl es solo informativo para la documentación (/docs).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
# Igual, pero no falla si no viene token (para rutas donde el login es opcional).
oauth2_scheme_opcional = OAuth2PasswordBearer(tokenUrl="api/login", auto_error=False)


def _usuario_desde_token(token: str, db: Session) -> User | None:
    payload = decode_access_token(token)
    if payload is None:
        return None

    email = payload.get("sub")
    if email is None:
        return None

    return db.query(User).filter(User.email == email).first()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Obliga a estar autenticado. Devuelve el usuario o lanza 401."""
    usuario = _usuario_desde_token(token, db)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado o token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario


def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_opcional),
    db: Session = Depends(get_db),
) -> User | None:
    """Autenticación opcional: devuelve el usuario si hay un token válido, o
    None si no viene token (o es inválido). No lanza error."""
    if token is None:
        return None
    return _usuario_desde_token(token, db)
