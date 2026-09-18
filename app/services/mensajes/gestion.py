from sqlalchemy.orm import Session

from app.models.mensaje import Mensaje
from app.models.user import User
from app.services.auth.roles import ROLES_GESTION


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
    # Valida que el destinatario exista y sea dignatario (admin/superadmin).
    destino = db.query(User).filter(User.id == destinatario_id).first()
    if destino is None:
        raise ValueError("El destinatario no existe")
    if destino.role not in ROLES_GESTION:
        raise ValueError("Solo se puede escribir a administradores o superadministradores")

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


def _participa(mensaje: Mensaje, usuario_id: int) -> bool:
    return usuario_id in (mensaje.remitente_id, mensaje.destinatario_id)


def eliminar_mensaje(db: Session, mensaje_id: int, usuario_id: int) -> bool:
    mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    # Cualquiera de los dos participantes puede eliminarlo.
    if mensaje is None or not _participa(mensaje, usuario_id):
        return False
    db.delete(mensaje)
    db.commit()
    return True


def editar_mensaje(db: Session, mensaje_id: int, usuario_id: int, contenido: str):
    from datetime import datetime, timedelta

    mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if mensaje is None:
        return None, "no_existe"
    # Solo el autor puede editar, y solo dentro de los 15 minutos.
    if mensaje.remitente_id != usuario_id:
        return None, "no_autorizado"
    if datetime.utcnow() - mensaje.created_at > timedelta(minutes=15):
        return None, "fuera_de_tiempo"

    mensaje.contenido = contenido
    mensaje.editado = True
    db.commit()
    db.refresh(mensaje)
    return mensaje, None


def fijar_mensaje(db: Session, mensaje_id: int, usuario_id: int, fijado: bool):
    mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if mensaje is None or not _participa(mensaje, usuario_id):
        return None
    mensaje.fijado = fijado
    db.commit()
    db.refresh(mensaje)
    return mensaje
