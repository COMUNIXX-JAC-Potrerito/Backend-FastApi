"""Consultas de PQRS a la base de datos."""

from sqlalchemy.orm import Query, Session, selectinload

from app.core.errores import NoEncontrado
from app.models.pqrs import PQRS
from app.services.pqrs.catalogos import ESTADO_NUEVA

MENSAJE_NO_EXISTE = "No existe la PQRS indicada"


def _con_respuestas(db: Session) -> Query:
    """Carga el hilo de respuestas en una sola consulta (evita N+1 al listar)."""
    return db.query(PQRS).options(selectinload(PQRS.respuestas))


def obtener_entrantes(db: Session) -> list[PQRS]:
    """PQRS nuevas y sin comité (por triar), de la más antigua a la más nueva."""
    return (
        _con_respuestas(db)
        .filter(PQRS.estado == ESTADO_NUEVA, PQRS.comite.is_(None))
        .order_by(PQRS.created_at.asc(), PQRS.id.asc())
        .all()
    )


def obtener_todas(db: Session) -> list[PQRS]:
    """Historial completo, de la más reciente a la más antigua."""
    return _con_respuestas(db).order_by(PQRS.created_at.desc(), PQRS.id.desc()).all()


def obtener_mias(db: Session, usuario_id: int) -> list[PQRS]:
    return (
        _con_respuestas(db)
        .filter(PQRS.radicado_por_id == usuario_id)
        .order_by(PQRS.created_at.desc(), PQRS.id.desc())
        .all()
    )


def obtener_asignadas(db: Session, comite: str) -> list[PQRS]:
    return (
        _con_respuestas(db)
        .filter(PQRS.comite == comite)
        .order_by(PQRS.created_at.desc(), PQRS.id.desc())
        .all()
    )


def obtener_por_id(db: Session, pqrs_id: int) -> PQRS:
    """La PQRS con ese id; lanza NoEncontrado si no existe."""
    pqrs = db.get(PQRS, pqrs_id)
    if pqrs is None:
        raise NoEncontrado(MENSAJE_NO_EXISTE)
    return pqrs


def obtener_por_codigo(db: Session, codigo: str) -> PQRS | None:
    return db.query(PQRS).filter(PQRS.codigo_seguimiento == codigo).first()
