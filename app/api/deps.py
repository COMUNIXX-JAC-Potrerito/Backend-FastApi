"""Dependencias de FastAPI para autenticación y autorización."""

from datetime import UTC

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.errores import NoAutenticado, SinPermiso
from app.db.session import get_db
from app.models.user import User
from app.services.auth.roles import ROL_SUPERADMIN, ROLES_GESTION
from app.services.auth.tokens import decode_access_token

# Lee "Authorization: Bearer <token>". tokenUrl solo sirve para la documentación.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
# Igual, pero sin fallar cuando no viene token (rutas con sesión opcional).
oauth2_scheme_opcional = OAuth2PasswordBearer(tokenUrl="api/login", auto_error=False)


def _token_anterior_al_cambio(payload: dict, usuario: User) -> bool:
    """True si el token se emitió antes del último cambio de contraseña del usuario.

    Así, al restablecer la contraseña se invalidan las sesiones abiertas antes. Se
    compara en segundos enteros (como el `iat` del JWT) para no tumbar un token
    emitido en el mismo segundo del cambio.
    """
    cambio = usuario.password_changed_at
    if cambio is None:
        return False
    iat = payload.get("iat")
    if not isinstance(iat, int | float):
        return False
    return iat < int(cambio.replace(tzinfo=UTC).timestamp())


def _usuario_desde_token(token: str, db: Session) -> User | None:
    """Usuario dueño del token, solo si el token es válido y la cuenta sigue activa."""
    payload = decode_access_token(token)
    email = payload.get("sub") if payload else None
    if not isinstance(email, str):
        return None
    usuario = db.query(User).filter(User.email == email).first()
    if usuario is None or not usuario.esta_activo:
        return None
    if _token_anterior_al_cambio(payload, usuario):
        return None
    return usuario


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Exige sesión: devuelve el usuario o responde 401."""
    usuario = _usuario_desde_token(token, db)
    if usuario is None:
        raise NoAutenticado("No autenticado o token inválido")
    return usuario


def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_opcional),
    db: Session = Depends(get_db),
) -> User | None:
    """Sesión opcional: el usuario si hay un token válido; None en otro caso."""
    if token is None:
        return None
    return _usuario_desde_token(token, db)


def requiere_roles(*roles_permitidos: str):
    """Crea una dependencia que exige sesión y uno de los roles indicados (403 si no)."""

    def verificador(usuario: User = Depends(get_current_user)) -> User:
        if usuario.role not in roles_permitidos:
            raise SinPermiso("No tienes permiso para realizar esta acción")
        return usuario

    return verificador


solo_dignatarios = requiere_roles(*ROLES_GESTION)
solo_superadmin = requiere_roles(ROL_SUPERADMIN)
