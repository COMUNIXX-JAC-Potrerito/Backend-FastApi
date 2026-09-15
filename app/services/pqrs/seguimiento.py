from sqlalchemy.orm import Session

from app.services.pqrs.consultas import obtener_por_codigo


def consultar_por_codigo(db: Session, codigo: str):
    """Consulta pública del estado de una PQRS por su código de seguimiento.
    Devuelve solo datos NO sensibles (nunca la identidad de quien la radicó),
    para que incluso las anónimas puedan seguirse sin revelar quién es."""
    pqrs = obtener_por_codigo(db, codigo)
    if pqrs is None:
        return None

    return {
        "codigo_seguimiento": pqrs.codigo_seguimiento,
        "tipo": pqrs.tipo,
        "asunto": pqrs.asunto,
        "estado": pqrs.estado,
        "comite": pqrs.comite,
        "created_at": pqrs.created_at,
        "updated_at": pqrs.updated_at,
    }
