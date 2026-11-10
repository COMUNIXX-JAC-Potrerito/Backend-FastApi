"""Mensajería interna entre dignatarios."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.errores import DatosInvalidos, NoEncontrado, SinPermiso
from app.core.tiempo import ahora_utc
from app.models.mensaje import Mensaje
from app.models.user import User
from app.schemas.mensaje import MensajeCreate
from app.services.auth.roles import es_dignatario

VENTANA_EDICION = timedelta(minutes=15)
MENSAJE_NO_EXISTE = "Mensaje no encontrado"


def _validar_no_vacio(contenido: str, adjunto_url: str | None) -> None:
    """Un mensaje debe tener texto o un adjunto."""
    if not contenido.strip() and not adjunto_url:
        raise DatosInvalidos("El mensaje no puede estar vacío")


def _obtener(db: Session, mensaje_id: int) -> Mensaje:
    mensaje = db.get(Mensaje, mensaje_id)
    if mensaje is None:
        raise NoEncontrado(MENSAJE_NO_EXISTE)
    return mensaje


def _obtener_si_participa(db: Session, mensaje_id: int, usuario_id: int) -> Mensaje:
    """El mensaje si el usuario es remitente o destinatario; si no, 404 (no revela que existe)."""
    mensaje = _obtener(db, mensaje_id)
    if usuario_id not in (mensaje.remitente_id, mensaje.destinatario_id):
        raise NoEncontrado(MENSAJE_NO_EXISTE)
    return mensaje


def _guardar(db: Session, mensaje: Mensaje) -> Mensaje:
    db.commit()
    db.refresh(mensaje)
    return mensaje


def enviar_mensaje(db: Session, remitente_id: int, datos: MensajeCreate) -> Mensaje:
    """Crea un mensaje para otro dignatario."""
    destino = db.get(User, datos.destinatario_id)
    if destino is None:
        raise DatosInvalidos("El destinatario no existe")
    if not es_dignatario(destino.role):
        raise DatosInvalidos("Solo se puede escribir a administradores o superadministradores")
    _validar_no_vacio(datos.contenido, datos.adjunto_url)

    mensaje = Mensaje(remitente_id=remitente_id, **datos.model_dump())
    db.add(mensaje)
    return _guardar(db, mensaje)


def recibidos(db: Session, usuario_id: int) -> list[Mensaje]:
    return (
        db.query(Mensaje)
        .filter(Mensaje.destinatario_id == usuario_id)
        .order_by(Mensaje.created_at.desc(), Mensaje.id.desc())
        .all()
    )


def enviados(db: Session, usuario_id: int) -> list[Mensaje]:
    return (
        db.query(Mensaje)
        .filter(Mensaje.remitente_id == usuario_id)
        .order_by(Mensaje.created_at.desc(), Mensaje.id.desc())
        .all()
    )


def marcar_leido(db: Session, mensaje_id: int, usuario_id: int) -> Mensaje:
    """Solo el destinatario puede marcarlo como leído."""
    mensaje = _obtener(db, mensaje_id)
    if mensaje.destinatario_id != usuario_id:
        raise NoEncontrado(MENSAJE_NO_EXISTE)
    mensaje.leido = True
    return _guardar(db, mensaje)


def editar_mensaje(db: Session, mensaje_id: int, usuario_id: int, contenido: str) -> Mensaje:
    """Solo el autor, dentro de los 15 minutos, y sin dejarlo vacío."""
    mensaje = _obtener(db, mensaje_id)
    if mensaje.remitente_id != usuario_id:
        raise SinPermiso("Solo el autor puede editar")
    if ahora_utc() - mensaje.created_at > VENTANA_EDICION:
        raise DatosInvalidos("Ya pasaron los 15 minutos para editar")
    _validar_no_vacio(contenido, mensaje.adjunto_url)
    mensaje.contenido = contenido
    mensaje.editado = True
    return _guardar(db, mensaje)


def fijar_mensaje(db: Session, mensaje_id: int, usuario_id: int, fijado: bool) -> Mensaje:
    mensaje = _obtener_si_participa(db, mensaje_id, usuario_id)
    mensaje.fijado = fijado
    return _guardar(db, mensaje)


def eliminar_mensaje(db: Session, mensaje_id: int, usuario_id: int) -> None:
    """Cualquiera de los dos participantes puede borrarlo (para ambos)."""
    db.delete(_obtener_si_participa(db, mensaje_id, usuario_id))
    db.commit()
