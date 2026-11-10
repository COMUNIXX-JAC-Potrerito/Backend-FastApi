"""Indicadores para el panel de información general."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.comunicacion import Comunicacion
from app.models.mensaje import Mensaje
from app.models.pqrs import PQRS
from app.models.publicacion import Publicacion
from app.models.user import User
from app.services.pqrs.catalogos import (
    COMITES_VALIDOS,
    ESTADO_EN_ESPERA,
    ESTADO_EN_PROCESO,
    ESTADO_FINALIZADA,
    ESTADO_NUEVA,
)


def _pqrs_por_estado(db: Session) -> dict[str, int]:
    return dict(db.query(PQRS.estado, func.count()).group_by(PQRS.estado).all())


def _comunicaciones_por_tipo(db: Session) -> dict[str, int]:
    return dict(db.query(Comunicacion.tipo, func.count()).group_by(Comunicacion.tipo).all())


def resumen(db: Session) -> dict:
    """Conteos generales de la gestión de la JAC."""
    por_estado = _pqrs_por_estado(db)
    por_tipo = _comunicaciones_por_tipo(db)
    return {
        "usuarios": db.query(User).count(),
        "pqrs_total": sum(por_estado.values()),
        "pqrs_nuevas": por_estado.get(ESTADO_NUEVA, 0),
        "pqrs_en_proceso": por_estado.get(ESTADO_EN_PROCESO, 0),
        "pqrs_en_espera": por_estado.get(ESTADO_EN_ESPERA, 0),
        "pqrs_finalizadas": por_estado.get(ESTADO_FINALIZADA, 0),
        "publicaciones": db.query(Publicacion).count(),
        "comunicaciones_enviadas": por_tipo.get("enviada", 0),
        "comunicaciones_recibidas": por_tipo.get("recibida", 0),
        "mensajes_internos": db.query(Mensaje).count(),
    }


def carga_por_comite(db: Session) -> list[dict]:
    """Total, en proceso, finalizadas y pendientes por comité (una sola consulta).

    Solo aparecen los comités con al menos una PQRS; primero los de más pendientes.
    """
    filas = (
        db.query(PQRS.comite, PQRS.estado, func.count())
        .filter(PQRS.comite.in_(COMITES_VALIDOS))
        .group_by(PQRS.comite, PQRS.estado)
        .all()
    )
    conteos: dict[str, dict[str, int]] = {}
    for comite, estado, cantidad in filas:
        conteos.setdefault(comite, {})[estado] = cantidad

    carga = []
    for comite in COMITES_VALIDOS:  # orden estable del catálogo para empates
        if comite not in conteos:
            continue
        por_estado = conteos[comite]
        total = sum(por_estado.values())
        finalizadas = por_estado.get(ESTADO_FINALIZADA, 0)
        carga.append(
            {
                "comite": comite,
                "total": total,
                "en_proceso": por_estado.get(ESTADO_EN_PROCESO, 0),
                "finalizadas": finalizadas,
                "pendientes": total - finalizadas,
            }
        )
    carga.sort(key=lambda fila: fila["pendientes"], reverse=True)
    return carga
