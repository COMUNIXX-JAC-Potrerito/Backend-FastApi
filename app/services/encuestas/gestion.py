"""Creación y gestión de encuestas/censos por parte de los dignatarios."""

import json

from sqlalchemy.orm import Session

from app.models.encuesta import Encuesta, Pregunta, RespuestaEncuesta, RespuestaItem

TIPOS_ENCUESTA = ["encuesta", "censo"]
TIPOS_PREGUNTA = ["texto", "opciones"]


def crear_encuesta(db: Session, titulo, descripcion, tipo, preguntas, created_by_id):
    if tipo not in TIPOS_ENCUESTA:
        raise ValueError("El tipo debe ser 'encuesta' o 'censo'")
    if not preguntas:
        raise ValueError("Debe incluir al menos una pregunta")

    encuesta = Encuesta(
        titulo=titulo,
        descripcion=descripcion,
        tipo=tipo,
        created_by_id=created_by_id,
    )
    db.add(encuesta)
    db.flush()  # obtiene el id sin cerrar la transacción

    for i, p in enumerate(preguntas):
        if p.tipo not in TIPOS_PREGUNTA:
            raise ValueError("El tipo de pregunta debe ser 'texto' u 'opciones'")
        opciones_json = None
        if p.tipo == "opciones":
            limpias = [o.strip() for o in (p.opciones or []) if o and o.strip()]
            if len(limpias) < 2:
                raise ValueError("Las preguntas de opción múltiple necesitan al menos 2 opciones")
            opciones_json = json.dumps(limpias, ensure_ascii=False)
        db.add(
            Pregunta(
                encuesta_id=encuesta.id,
                texto=p.texto,
                tipo=p.tipo,
                opciones=opciones_json,
                orden=i,
            )
        )

    db.commit()
    db.refresh(encuesta)
    return encuesta


def listar_encuestas(db: Session, solo_publicadas: bool):
    query = db.query(Encuesta)
    if solo_publicadas:
        query = query.filter(Encuesta.publicada.is_(True))
    return query.order_by(Encuesta.created_at.desc()).all()


def obtener_preguntas(db: Session, encuesta_id: int):
    return (
        db.query(Pregunta)
        .filter(Pregunta.encuesta_id == encuesta_id)
        .order_by(Pregunta.orden)
        .all()
    )


def obtener_encuesta(db: Session, encuesta_id: int):
    return db.query(Encuesta).filter(Encuesta.id == encuesta_id).first()


def publicar_encuesta(db: Session, encuesta_id: int, publicada: bool):
    encuesta = obtener_encuesta(db, encuesta_id)
    if encuesta is None:
        return None
    encuesta.publicada = publicada
    db.commit()
    db.refresh(encuesta)
    return encuesta


def eliminar_encuesta(db: Session, encuesta_id: int) -> bool:
    encuesta = obtener_encuesta(db, encuesta_id)
    if encuesta is None:
        return False

    resp_ids = [
        r.id
        for r in db.query(RespuestaEncuesta)
        .filter(RespuestaEncuesta.encuesta_id == encuesta_id)
        .all()
    ]
    if resp_ids:
        db.query(RespuestaItem).filter(RespuestaItem.respuesta_id.in_(resp_ids)).delete(
            synchronize_session=False
        )
    db.query(RespuestaEncuesta).filter(RespuestaEncuesta.encuesta_id == encuesta_id).delete(
        synchronize_session=False
    )
    db.query(Pregunta).filter(Pregunta.encuesta_id == encuesta_id).delete(
        synchronize_session=False
    )
    db.delete(encuesta)
    db.commit()
    return True


def opciones_a_lista(opciones_json: str | None) -> list[str] | None:
    if not opciones_json:
        return None
    try:
        return json.loads(opciones_json)
    except (ValueError, TypeError):
        return None
