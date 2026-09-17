from sqlalchemy.orm import Session

from app.models.comunicacion import Comunicacion
from app.models.mensaje import Mensaje
from app.models.pqrs import PQRS
from app.models.publicacion import Publicacion
from app.models.user import User


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
