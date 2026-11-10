"""Consulta pública del estado de una PQRS por su código de seguimiento."""

from sqlalchemy.orm import Session

from app.core.errores import NoEncontrado
from app.services.pqrs.anonimato import nombre_adjunto_visible, respuestas_de
from app.services.pqrs.consultas import obtener_por_codigo


def consultar_por_codigo(db: Session, codigo: str) -> dict:
    """Solo datos no sensibles: nunca la identidad de quien la radicó."""
    pqrs = obtener_por_codigo(db, codigo)
    if pqrs is None:
        raise NoEncontrado("No existe una PQRS con ese código de seguimiento")
    return {
        "codigo_seguimiento": pqrs.codigo_seguimiento,
        "tipo": pqrs.tipo,
        "asunto": pqrs.asunto,
        "estado": pqrs.estado,
        "comite": pqrs.comite,
        "created_at": pqrs.created_at,
        "updated_at": pqrs.updated_at,
        "respuesta": pqrs.respuesta,
        "respuestas": respuestas_de(pqrs),
        "adjunto_url": pqrs.adjunto_url,
        "adjunto_tipo": pqrs.adjunto_tipo,
        "adjunto_nombre": nombre_adjunto_visible(pqrs),
    }
