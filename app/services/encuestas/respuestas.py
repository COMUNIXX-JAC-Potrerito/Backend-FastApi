"""Respuestas de la comunidad a las encuestas y cálculo de resultados."""

import json
from collections import Counter
from dataclasses import dataclass

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.errores import Conflicto, DatosInvalidos, SinPermiso
from app.models.encuesta import Pregunta, RespuestaEncuesta, RespuestaItem
from app.models.user import User
from app.schemas.encuesta import ResponderEncuesta, RespuestaItemCreate
from app.services.auth.gestion import buscar_por_email
from app.services.auth.validaciones import normalizar_email
from app.services.encuestas.gestion import TIPO_OPCIONES, obtener_encuesta


@dataclass(frozen=True)
class Participante:
    usuario_id: int | None
    nombre: str | None
    email: str | None
    telefono: str | None


def _limpio(valor: str | None) -> str | None:
    return valor.strip() if valor and valor.strip() else None


def participante_desde(datos: ResponderEncuesta, usuario: User | None) -> Participante:
    """Con sesión se usan los datos de la cuenta (el teléfono se completa si falta)."""
    if usuario is not None:
        return Participante(
            usuario_id=usuario.id,
            nombre=usuario.full_name,
            email=usuario.email,
            telefono=usuario.phone or _limpio(datos.telefono),
        )
    email = _limpio(datos.email)
    return Participante(
        usuario_id=None,
        nombre=_limpio(datos.nombre),
        email=normalizar_email(email) if email else None,
        telefono=_limpio(datos.telefono),
    )


def _ya_respondio(db: Session, encuesta_id: int, participante: Participante) -> bool:
    """Cuenta como repetida si coincide la cuenta o el correo (aunque se omita el token)."""
    criterios = []
    if participante.usuario_id is not None:
        criterios.append(RespuestaEncuesta.usuario_id == participante.usuario_id)
    if participante.email:
        criterios.append(func.lower(RespuestaEncuesta.email) == normalizar_email(participante.email))
    if not criterios:
        return False
    return (
        db.query(RespuestaEncuesta.id)
        .filter(RespuestaEncuesta.encuesta_id == encuesta_id, or_(*criterios))
        .first()
        is not None
    )


def _validar_items(preguntas: list[Pregunta], items: list[RespuestaItemCreate]) -> None:
    """Cada ítem debe ser de esta encuesta, sin repetir, y con una opción existente."""
    por_id = {p.id: p for p in preguntas}
    vistos: set[int] = set()
    for item in items:
        pregunta = por_id.get(item.pregunta_id)
        if pregunta is None:
            raise DatosInvalidos("La respuesta incluye preguntas que no pertenecen a esta encuesta")
        if item.pregunta_id in vistos:
            raise DatosInvalidos("Cada pregunta se responde una sola vez")
        vistos.add(item.pregunta_id)
        if pregunta.tipo == TIPO_OPCIONES and not _opcion_valida(pregunta, item.valor):
            raise DatosInvalidos("La opción elegida no es válida para la pregunta")


def _opcion_valida(pregunta: Pregunta, valor: str | None) -> bool:
    """Una pregunta de opciones puede quedar sin responder o tener una opción existente."""
    elegida = _limpio(valor)
    return elegida is None or elegida in json.loads(pregunta.opciones or "[]")


def responder_encuesta(
    db: Session, encuesta_id: int, items: list[RespuestaItemCreate], participante: Participante
) -> RespuestaEncuesta:
    encuesta = obtener_encuesta(db, encuesta_id)
    if not encuesta.publicada:
        raise DatosInvalidos("La encuesta no está publicada")
    if _ya_respondio(db, encuesta_id, participante):
        raise Conflicto("Ya respondiste esta encuesta")
    if participante.usuario_id is None and participante.email and buscar_por_email(db, participante.email):
        # Evita responder en nombre de otra persona (y bloquearle su propia respuesta).
        raise SinPermiso("Ese correo pertenece a una cuenta registrada: inicia sesión para responder")
    if not participante.nombre or not (participante.email or participante.telefono):
        raise DatosInvalidos("Indica tu nombre y un correo o teléfono para responder")
    _validar_items(encuesta.preguntas, items)

    respuesta = RespuestaEncuesta(
        encuesta_id=encuesta_id,
        usuario_id=participante.usuario_id,
        nombre=participante.nombre,
        email=participante.email,
        telefono=participante.telefono,
    )
    db.add(respuesta)
    db.flush()
    db.add_all(
        RespuestaItem(respuesta_id=respuesta.id, pregunta_id=i.pregunta_id, valor=i.valor) for i in items
    )
    db.commit()
    db.refresh(respuesta)
    return respuesta


def _resultado_pregunta(pregunta: Pregunta, valores: list[str]) -> dict:
    es_opciones = pregunta.tipo == TIPO_OPCIONES
    return {
        "pregunta_id": pregunta.id,
        "texto": pregunta.texto,
        "tipo": pregunta.tipo,
        "total": len(valores),
        "conteo": dict(Counter(valores)) if es_opciones else None,
        "respuestas_texto": None if es_opciones else valores,
    }


def resultados(db: Session, encuesta_id: int) -> dict:
    """Conteo por opción o lista de textos, por cada pregunta."""
    encuesta = obtener_encuesta(db, encuesta_id)
    total = db.query(RespuestaEncuesta).filter(RespuestaEncuesta.encuesta_id == encuesta_id).count()
    filas = (
        db.query(RespuestaItem.pregunta_id, RespuestaItem.valor)
        .join(RespuestaEncuesta, RespuestaItem.respuesta_id == RespuestaEncuesta.id)
        .filter(RespuestaEncuesta.encuesta_id == encuesta_id)
        .all()
    )
    por_pregunta: dict[int, list[str]] = {}
    for pregunta_id, valor in filas:
        if valor and valor.strip():
            por_pregunta.setdefault(pregunta_id, []).append(valor)

    return {
        "encuesta_id": encuesta.id,
        "titulo": encuesta.titulo,
        "total_respuestas": total,
        "preguntas": [_resultado_pregunta(p, por_pregunta.get(p.id, [])) for p in encuesta.preguntas],
    }


def encuestas_respondidas_por(db: Session, usuario_id: int) -> list[int]:
    """IDs de las encuestas que el usuario ya respondió."""
    filas = (
        db.query(RespuestaEncuesta.encuesta_id)
        .filter(RespuestaEncuesta.usuario_id == usuario_id)
        .distinct()
        .all()
    )
    return [encuesta_id for (encuesta_id,) in filas]


def participantes(db: Session, encuesta_id: int) -> list[RespuestaEncuesta]:
    """Quién respondió la encuesta, más recientes primero."""
    obtener_encuesta(db, encuesta_id)
    return (
        db.query(RespuestaEncuesta)
        .filter(RespuestaEncuesta.encuesta_id == encuesta_id)
        .order_by(RespuestaEncuesta.created_at.desc(), RespuestaEncuesta.id.desc())
        .all()
    )
