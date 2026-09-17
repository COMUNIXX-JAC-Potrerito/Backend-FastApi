from sqlalchemy.orm import Session

from app.models.mensaje import Mensaje
from app.models.user import User


def enviar_mensaje(
    db: Session,
    remitente_id: int,
    destinatario_id: int,
    asunto: str,
    contenido: str,
    adjunto_url: str | None = None,
    adjunto_tipo: str | None = None,
    adjunto_nombre: str | None = None,
):
    # Valida que el destinatario exista
    destino = db.query(User).filter(User.id == destinatario_id).first()
    if destino is None:
        raise ValueError("El destinatario no existe")

    # Un mensaje debe tener texto o un adjunto (no puede ir totalmente vacío)
    if not contenido.strip() and not adjunto_url:
        raise ValueError("El mensaje no puede estar vacío")

    mensaje = Mensaje(
        remitente_id=remitente_id,
        destinatario_id=destinatario_id,
        asunto=asunto,
        contenido=contenido,
        adjunto_url=adjunto_url,
        adjunto_tipo=adjunto_tipo,
        adjunto_nombre=adjunto_nombre,
    )
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)
    return mensaje


def recibidos(db: Session, usuario_id: int):
    return (
        db.query(Mensaje)
        .filter(Mensaje.destinatario_id == usuario_id)
        .order_by(Mensaje.created_at.desc())
        .all()
    )


def enviados(db: Session, usuario_id: int):
    return (
        db.query(Mensaje)
        .filter(Mensaje.remitente_id == usuario_id)
        .order_by(Mensaje.created_at.desc())
        .all()
    )


def marcar_leido(db: Session, mensaje_id: int, usuario_id: int):
    mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if mensaje is None or mensaje.destinatario_id != usuario_id:
        return None
    mensaje.leido = True
    db.commit()
    db.refresh(mensaje)
    return mensaje
