from sqlalchemy.orm import Session

from app.models.pqrs import PQRS


def obtener_entrantes(db: Session):
    """Devuelve las PQRS nuevas y AÚN SIN comité (bandeja de entrantes, por triar)."""
    # Al asignarles comité salen de aquí y pasan a "Mis asignadas" del comité.
    return (
        db.query(PQRS)
        .filter(PQRS.estado == "Nueva", PQRS.comite.is_(None))
        .all()
    )


def obtener_todas(db: Session):
    """Devuelve TODAS las PQRS, de la más reciente a la más antigua (historial)."""
    return db.query(PQRS).order_by(PQRS.created_at.desc()).all()


def obtener_por_id(db: Session, pqrs_id: int):
    """Busca una PQRS por su id; devuelve None si no existe."""
    return db.query(PQRS).filter(PQRS.id == pqrs_id).first()


def obtener_por_codigo(db: Session, codigo: str):
    """Busca una PQRS por su código de seguimiento; None si no existe."""
    return db.query(PQRS).filter(PQRS.codigo_seguimiento == codigo).first()


def obtener_mias(db: Session, usuario_id: int):
    """Devuelve las PQRS que radicó un usuario (su FK), más recientes primero."""
    return (
        db.query(PQRS)
        .filter(PQRS.radicado_por_id == usuario_id)
        .order_by(PQRS.created_at.desc())
        .all()
    )


def obtener_asignadas(db: Session, comite: str):
    """Devuelve las PQRS asignadas a un comité/comisión, más recientes primero."""
    return (
        db.query(PQRS)
        .filter(PQRS.comite == comite)
        .order_by(PQRS.created_at.desc())
        .all()
    )
