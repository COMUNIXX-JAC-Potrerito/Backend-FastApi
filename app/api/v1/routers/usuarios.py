"""Usuarios: listado para dignatarios; roles y comisiones solo para superadmin."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import solo_dignatarios, solo_superadmin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import CambiarComite, CambiarRol, UserResponse
from app.services.usuarios import gestion

router = APIRouter(tags=["usuarios"])


@router.get("/usuarios", response_model=list[UserResponse], dependencies=[Depends(solo_dignatarios)])
def listar_usuarios(db: Session = Depends(get_db)):
    """Usuarios registrados (para elegir destinatarios, gestionar roles, etc.)."""
    return gestion.listar_usuarios(db)


@router.put("/usuarios/{user_id}/rol", response_model=UserResponse)
def actualizar_rol(
    user_id: int, data: CambiarRol, db: Session = Depends(get_db), usuario: User = Depends(solo_superadmin)
):
    return gestion.cambiar_rol(db, user_id, data.rol, usuario.id)


@router.put("/usuarios/{user_id}/comite", response_model=UserResponse)
def actualizar_comite(
    user_id: int, data: CambiarComite, db: Session = Depends(get_db), usuario: User = Depends(solo_superadmin)
):
    return gestion.cambiar_comite(db, user_id, data.comite, usuario.id)
