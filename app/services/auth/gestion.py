"""Registro de usuarios e inicio de sesión."""

from functools import lru_cache

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.errores import DatosInvalidos, NoAutenticado
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth.seguridad import hash_password, verify_password
from app.services.auth.tokens import create_access_token
from app.services.auth.validaciones import is_password_strong, is_valid_email, normalizar_email

MENSAJE_CREDENCIALES = "Correo o contraseña incorrectos"


@lru_cache(maxsize=1)
def _hash_ficticio() -> str:
    """Hash usado cuando el correo no existe, para que la respuesta tarde lo mismo
    y no se pueda averiguar qué correos están registrados midiendo el tiempo."""
    return hash_password("contraseña-ficticia-solo-para-igualar-tiempos")


def buscar_por_email(db: Session, email: str) -> User | None:
    """Busca un usuario sin distinguir mayúsculas (cubre correos antiguos sin normalizar)."""
    return db.query(User).filter(func.lower(User.email) == normalizar_email(email)).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Devuelve el usuario si las credenciales son correctas y la cuenta está activa."""
    user = buscar_por_email(db, email)
    if user is None:
        verify_password(password, _hash_ficticio())
        return None
    if not verify_password(password, user.hashed_password) or not user.esta_activo:
        return None
    return user


def login_user(db: Session, email: str, password: str) -> str:
    """Devuelve un JWT para el usuario; lanza NoAutenticado si no se puede ingresar."""
    user = authenticate_user(db, email, password)
    if user is None:
        raise NoAutenticado(MENSAJE_CREDENCIALES)
    return create_access_token({"sub": user.email, "role": user.role})


def register_user(db: Session, datos: UserCreate) -> User:
    """Crea una cuenta con rol "usuario" (el rol lo asigna después un superadmin)."""
    email = normalizar_email(datos.email)
    if not is_valid_email(email):
        raise DatosInvalidos("El correo no tiene un formato válido")
    if not is_password_strong(datos.password):
        raise DatosInvalidos("La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número")
    if buscar_por_email(db, email) is not None:
        raise DatosInvalidos("Ya existe un usuario registrado con ese correo")

    usuario = User(
        full_name=datos.full_name.strip(),
        email=email,
        hashed_password=hash_password(datos.password),
        phone=datos.phone,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
