from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.mensaje import (
    EditarMensaje,
    FijarMensaje,
    MensajeCreate,
    MensajeResponse,
)
from app.services.auth.roles import ROLES_GESTION
from app.services.mensajes.gestion import (
    editar_mensaje,
    eliminar_mensaje,
    enviados,
    enviar_mensaje,
    fijar_mensaje,
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
        return enviar_mensaje(
            db,
            usuario.id,
            data.destinatario_id,
            data.asunto,
            data.contenido,
            adjunto_url=data.adjunto_url,
            adjunto_tipo=data.adjunto_tipo,
            adjunto_nombre=data.adjunto_nombre,
        )
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


@router.put("/mensajes/{mensaje_id}", response_model=MensajeResponse)
def editar(
    mensaje_id: int,
    data: EditarMensaje,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    mensaje, error = editar_mensaje(db, mensaje_id, usuario.id, data.contenido)
    if error == "no_existe":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")
    if error == "no_autorizado":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el autor puede editar")
    if error == "fuera_de_tiempo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya pasaron los 15 minutos para editar",
        )
    return mensaje


@router.put("/mensajes/{mensaje_id}/fijar", response_model=MensajeResponse)
def fijar(
    mensaje_id: int,
    data: FijarMensaje,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    mensaje = fijar_mensaje(db, mensaje_id, usuario.id, data.fijado)
    if mensaje is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")
    return mensaje


@router.delete("/mensajes/{mensaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    mensaje_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    if not eliminar_mensaje(db, mensaje_id, usuario.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")
