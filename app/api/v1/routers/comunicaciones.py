"""Bitácora de comunicaciones externas (solo dignatarios)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import solo_dignatarios
from app.db.session import get_db
from app.models.user import User
from app.schemas.comunicacion import ComunicacionCreate, ComunicacionResponse
from app.services.comunicaciones.gestion import eliminar, listar, registrar

router = APIRouter(tags=["comunicaciones"])


@router.post("/comunicaciones", response_model=ComunicacionResponse, status_code=status.HTTP_201_CREATED)
def crear(data: ComunicacionCreate, db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    """Registra una comunicación enviada o recibida."""
    return registrar(db, data, usuario.id)


@router.get(
    "/comunicaciones",
    response_model=list[ComunicacionResponse],
    dependencies=[Depends(solo_dignatarios)],
)
def obtener(tipo: str | None = None, db: Session = Depends(get_db)):
    return listar(db, tipo)


@router.delete(
    "/comunicaciones/{comunicacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(solo_dignatarios)],
)
def borrar(comunicacion_id: int, db: Session = Depends(get_db)):
    eliminar(db, comunicacion_id)
