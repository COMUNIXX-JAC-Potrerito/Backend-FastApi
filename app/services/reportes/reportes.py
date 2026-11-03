from sqlalchemy.orm import Session

from app.models.comunicacion import Comunicacion
from app.models.mensaje import Mensaje
from app.models.pqrs import PQRS
from app.models.publicacion import Publicacion
from app.models.user import User
from app.services.pqrs.catalogos import (
    COMITES_VALIDOS,
    ESTADO_EN_PROCESO,
    ESTADO_FINALIZADA,
)


def resumen(db: Session) -> dict:
    """Estadísticas generales de la gestión de la JAC."""
    return {
        "usuarios": db.query(User).count(),
        "pqrs_total": db.query(PQRS).count(),
        "pqrs_nuevas": db.query(PQRS).filter(PQRS.estado == "Nueva").count(),
        "pqrs_en_proceso": db.query(PQRS).filter(PQRS.estado == "En_Proceso").count(),
        "pqrs_finalizadas": db.query(PQRS).filter(PQRS.estado == "Finalizada").count(),
        "publicaciones": db.query(Publicacion).count(),
        "comunicaciones_enviadas": db.query(Comunicacion).filter(Comunicacion.tipo == "enviada").count(),
        "comunicaciones_recibidas": db.query(Comunicacion).filter(Comunicacion.tipo == "recibida").count(),
        "mensajes_internos": db.query(Mensaje).count(),
    }


def carga_por_comite(db: Session) -> list[dict]:
    """Trabajo de cada comité: total, en proceso, finalizadas y pendientes.

    Sirve para ver de un vistazo el flujo y la carga de cada comité en el
    panel de información general.
    """
    filas = []
    for comite in COMITES_VALIDOS:
        base = db.query(PQRS).filter(PQRS.comite == comite)
        total = base.count()
        if total == 0:
            continue  # no mostramos comités sin ninguna PQRS
        en_proceso = base.filter(PQRS.estado == ESTADO_EN_PROCESO).count()
        finalizadas = base.filter(PQRS.estado == ESTADO_FINALIZADA).count()
        filas.append(
            {
                "comite": comite,
                "total": total,
                "en_proceso": en_proceso,
                "finalizadas": finalizadas,
                "pendientes": total - finalizadas,
            }
        )
    # Los de mayor carga pendiente primero
    filas.sort(key=lambda f: f["pendientes"], reverse=True)
    return filas
