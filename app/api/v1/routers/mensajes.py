from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.mensaje import MensajeCreate, MensajeResponse
from app.services.auth.roles import ROLES_GESTION
from app.services.mensajes.gestion import (
    enviados,
    enviar_mensaje,
    marcar_leido,
    recibidos,
)

router = APIRouter()


@router.post("/mensajes", response_model=MensajeResponse, status_code=status.HTTP_201_CREATED)
def enviar(
    data: MensajeCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    try:
        return enviar_mensaje(db, usuario.id, data.destinatario_id, data.asunto, data.contenido)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/mensajes/recibidos", response_model=list[MensajeResponse])
def bandeja_entrada(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    return recibidos(db, usuario.id)


@router.get("/mensajes/enviados", response_model=list[MensajeResponse])
def bandeja_enviados(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    return enviados(db, usuario.id)


@router.put("/mensajes/{mensaje_id}/leido", response_model=MensajeResponse)
def leer(
    mensaje_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    mensaje = marcar_leido(db, mensaje_id, usuario.id)
    if mensaje is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")
    return mensaje
