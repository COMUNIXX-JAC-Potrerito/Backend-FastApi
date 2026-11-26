"""Registro de usuarios, inicio de sesión y recuperación de contraseña."""

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.limites import (
    ip_cliente,
    limite_login,
    limite_login_por_cuenta,
    limite_login_por_cuenta_e_ip,
    limite_recuperar,
    limite_registro,
)
from app.db.session import get_db
from app.schemas.recuperacion import RecuperarRequest, RestablecerRequest
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth.gestion import login_user, register_user
from app.services.auth.recuperacion import restablecer_password, solicitar_recuperacion
from app.services.auth.validaciones import normalizar_email

router = APIRouter(tags=["auth"])

_MENSAJE_RECUPERAR = "Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña."


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limite_registro)],
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Crea una cuenta de la comunidad (rol "usuario")."""
    return register_user(db, data)


@router.post("/login", response_model=Token, dependencies=[Depends(limite_login)])
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Devuelve un JWT si las credenciales son correctas."""
    cuenta = normalizar_email(credentials.email)
    limite_login_por_cuenta_e_ip.verificar(f"{cuenta}|{ip_cliente(request)}")
    limite_login_por_cuenta.verificar(cuenta)
    return {"access_token": login_user(db, credentials.email, credentials.password), "token_type": "bearer"}


@router.post("/recuperar", dependencies=[Depends(limite_recuperar)])
def recuperar(data: RecuperarRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Envía (si el correo existe) un enlace para restablecer la contraseña."""
    solicitar_recuperacion(db, data.email, background_tasks)
    return {"mensaje": _MENSAJE_RECUPERAR}


@router.post("/restablecer", dependencies=[Depends(limite_recuperar)])
def restablecer(data: RestablecerRequest, db: Session = Depends(get_db)):
    """Cambia la contraseña usando un token de recuperación válido."""
    restablecer_password(db, data.token, data.password)
    return {"mensaje": "Tu contraseña fue actualizada. Ya puedes iniciar sesión."}
