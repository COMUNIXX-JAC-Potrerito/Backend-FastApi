"""Creación y gestión de encuestas/censos por parte de los dignatarios."""

import json

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errores import DatosInvalidos, NoEncontrado
from app.models.encuesta import Encuesta, Pregunta, RespuestaEncuesta, RespuestaItem
from app.schemas.encuesta import EncuestaCreate, PreguntaCreate

TIPOS_ENCUESTA = ("encuesta", "censo")
TIPO_TEXTO = "texto"
TIPO_OPCIONES = "opciones"
TIPOS_PREGUNTA = (TIPO_TEXTO, TIPO_OPCIONES)
MIN_OPCIONES = 2
MENSAJE_NO_EXISTE = "Encuesta no encontrada"


def _opciones_limpias(pregunta: PreguntaCreate) -> list[str]:
    return [o.strip() for o in (pregunta.opciones or []) if o and o.strip()]


def _validar(datos: EncuestaCreate) -> None:
    """Valida todo antes de escribir, para no dejar encuestas a medias."""
    if datos.tipo not in TIPOS_ENCUESTA:
        raise DatosInvalidos("El tipo debe ser 'encuesta' o 'censo'")
    if not datos.preguntas:
        raise DatosInvalidos("Debe incluir al menos una pregunta")
    for pregunta in datos.preguntas:
        if pregunta.tipo not in TIPOS_PREGUNTA:
            raise DatosInvalidos("El tipo de pregunta debe ser 'texto' u 'opciones'")
        if pregunta.tipo == TIPO_OPCIONES and len(_opciones_limpias(pregunta)) < MIN_OPCIONES:
            raise DatosInvalidos("Las preguntas de opción múltiple necesitan al menos 2 opciones")


def _a_modelo(pregunta: PreguntaCreate, orden: int) -> Pregunta:
    opciones = None
    if pregunta.tipo == TIPO_OPCIONES:
        opciones = json.dumps(_opciones_limpias(pregunta), ensure_ascii=False)
    return Pregunta(texto=pregunta.texto, tipo=pregunta.tipo, opciones=opciones, orden=orden)


def crear_encuesta(db: Session, datos: EncuestaCreate, creado_por_id: int) -> Encuesta:
    _validar(datos)
    encuesta = Encuesta(
        titulo=datos.titulo,
        descripcion=datos.descripcion,
        tipo=datos.tipo,
        created_by_id=creado_por_id,
        preguntas=[_a_modelo(p, orden) for orden, p in enumerate(datos.preguntas)],
    )
    db.add(encuesta)
    db.commit()
    db.refresh(encuesta)
    return encuesta


def listar_encuestas(db: Session, solo_publicadas: bool) -> list[Encuesta]:
    """Encuestas (solo publicadas o todas), más recientes primero."""
    query = db.query(Encuesta)
    if solo_publicadas:
        query = query.filter(Encuesta.publicada.is_(True))
    return query.order_by(Encuesta.created_at.desc(), Encuesta.id.desc()).all()


def obtener_encuesta(db: Session, encuesta_id: int) -> Encuesta:
    """La encuesta con sus preguntas; lanza NoEncontrado si no existe."""
    encuesta = (
        db.query(Encuesta)
        .options(selectinload(Encuesta.preguntas))
        .filter(Encuesta.id == encuesta_id)
        .first()
    )
    if encuesta is None:
        raise NoEncontrado(MENSAJE_NO_EXISTE)
    return encuesta


def obtener_visible(db: Session, encuesta_id: int, es_dignatario: bool) -> Encuesta:
    """Las encuestas no publicadas solo las ven los dignatarios (para el resto, 404)."""
    encuesta = obtener_encuesta(db, encuesta_id)
    if not encuesta.publicada and not es_dignatario:
        raise NoEncontrado(MENSAJE_NO_EXISTE)
    return encuesta


def publicar_encuesta(db: Session, encuesta_id: int, publicada: bool) -> Encuesta:
    encuesta = obtener_encuesta(db, encuesta_id)
    encuesta.publicada = publicada
    db.commit()
    db.refresh(encuesta)
    return encuesta


def eliminar_encuesta(db: Session, encuesta_id: int) -> None:
    """Borra la encuesta con sus preguntas, respuestas e ítems."""
    encuesta = obtener_encuesta(db, encuesta_id)
    respuestas = select(RespuestaEncuesta.id).where(RespuestaEncuesta.encuesta_id == encuesta_id)
    db.query(RespuestaItem).filter(RespuestaItem.respuesta_id.in_(respuestas)).delete(
        synchronize_session=False
    )
    db.query(RespuestaEncuesta).filter(RespuestaEncuesta.encuesta_id == encuesta_id).delete(
        synchronize_session=False
    )
    db.delete(encuesta)  # las preguntas se borran en cascada
    db.commit()
