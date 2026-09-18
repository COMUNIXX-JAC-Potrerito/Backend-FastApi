"""Registro de respuestas de la comunidad y cálculo de resultados."""

from collections import Counter

from sqlalchemy.orm import Session

from app.models.encuesta import Encuesta, Pregunta, RespuestaEncuesta, RespuestaItem


def responder_encuesta(db: Session, encuesta_id: int, items, usuario_id):
    encuesta = db.query(Encuesta).filter(Encuesta.id == encuesta_id).first()
    if encuesta is None:
        return None, "no_existe"
    if not encuesta.publicada:
        return None, "no_publicada"

    respuesta = RespuestaEncuesta(encuesta_id=encuesta_id, usuario_id=usuario_id)
    db.add(respuesta)
    db.flush()

    for it in items:
        db.add(
            RespuestaItem(
                respuesta_id=respuesta.id,
                pregunta_id=it.pregunta_id,
                valor=it.valor,
            )
        )
    db.commit()
    db.refresh(respuesta)
    return respuesta, None


def resultados(db: Session, encuesta_id: int):
    encuesta = db.query(Encuesta).filter(Encuesta.id == encuesta_id).first()
    if encuesta is None:
        return None

    preguntas = (
        db.query(Pregunta)
        .filter(Pregunta.encuesta_id == encuesta_id)
        .order_by(Pregunta.orden)
        .all()
    )
    respuestas = (
        db.query(RespuestaEncuesta)
        .filter(RespuestaEncuesta.encuesta_id == encuesta_id)
        .all()
    )
    total_respuestas = len(respuestas)
    resp_ids = [r.id for r in respuestas]

    items = (
        db.query(RespuestaItem).filter(RespuestaItem.respuesta_id.in_(resp_ids)).all()
        if resp_ids
        else []
    )
    por_pregunta: dict[int, list[str]] = {}
    for it in items:
        por_pregunta.setdefault(it.pregunta_id, []).append(it.valor)

    detalle = []
    for p in preguntas:
        valores = [v for v in por_pregunta.get(p.id, []) if v and v.strip()]
        if p.tipo == "opciones":
            detalle.append(
                {
                    "pregunta_id": p.id,
                    "texto": p.texto,
                    "tipo": p.tipo,
                    "total": len(valores),
                    "conteo": dict(Counter(valores)),
                    "respuestas_texto": None,
                }
            )
        else:
            detalle.append(
                {
                    "pregunta_id": p.id,
                    "texto": p.texto,
                    "tipo": p.tipo,
                    "total": len(valores),
                    "conteo": None,
                    "respuestas_texto": valores,
                }
            )

    return {
        "encuesta_id": encuesta.id,
        "titulo": encuesta.titulo,
        "total_respuestas": total_respuestas,
        "preguntas": detalle,
    }
