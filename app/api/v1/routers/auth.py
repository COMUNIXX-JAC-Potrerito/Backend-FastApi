"""Registro de usuarios e inicio de sesión."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.limites import (
    ip_cliente,
    limite_login,
    limite_login_por_cuenta,
    limite_login_por_cuenta_e_ip,
    limite_registro,
)
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth.gestion import login_user, register_user
from app.services.auth.validaciones import normalizar_email

router = APIRouter(tags=["auth"])


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
