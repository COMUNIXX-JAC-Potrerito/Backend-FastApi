"""Mensajería interna entre dignatarios."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import solo_dignatarios
from app.db.session import get_db
from app.models.user import User
from app.schemas.mensaje import EditarMensaje, FijarMensaje, MensajeCreate, MensajeResponse
from app.services.mensajes import gestion

router = APIRouter(tags=["mensajes"])


@router.post("/mensajes", response_model=MensajeResponse, status_code=status.HTTP_201_CREATED)
def enviar(data: MensajeCreate, db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    """Envía un mensaje a otro dignatario (con adjunto opcional)."""
    return gestion.enviar_mensaje(db, usuario.id, data)


@router.get("/mensajes/recibidos", response_model=list[MensajeResponse])
def bandeja_entrada(db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    return gestion.recibidos(db, usuario.id)


@router.get("/mensajes/enviados", response_model=list[MensajeResponse])
def bandeja_enviados(db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    return gestion.enviados(db, usuario.id)


@router.put("/mensajes/{mensaje_id}/leido", response_model=MensajeResponse)
def leer(mensaje_id: int, db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    """Marca como leído un mensaje recibido."""
    return gestion.marcar_leido(db, mensaje_id, usuario.id)


@router.put("/mensajes/{mensaje_id}", response_model=MensajeResponse)
def editar(
    mensaje_id: int,
    data: EditarMensaje,
    db: Session = Depends(get_db),
    usuario: User = Depends(solo_dignatarios),
):
    """Edita un mensaje propio dentro de los 15 minutos siguientes."""
    return gestion.editar_mensaje(db, mensaje_id, usuario.id, data.contenido)


@router.put("/mensajes/{mensaje_id}/fijar", response_model=MensajeResponse)
def fijar(
    mensaje_id: int,
    data: FijarMensaje,
    db: Session = Depends(get_db),
    usuario: User = Depends(solo_dignatarios),
):
    """Fija o desfija un mensaje de la conversación."""
    return gestion.fijar_mensaje(db, mensaje_id, usuario.id, data.fijado)


@router.delete("/mensajes/{mensaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(mensaje_id: int, db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    """Elimina un mensaje en el que el usuario participa."""
    gestion.eliminar_mensaje(db, mensaje_id, usuario.id)
