from sqlalchemy.orm import Session

from app.models.pqrs import PQRS


def obtener_entrantes(db: Session):
    # "Entrantes" = solicitudes nuevas AÚN SIN asignar a un comité (por triar).
    # Al asignarles comité salen de aquí y pasan a "Mis asignadas" del comité.
    return (
        db.query(PQRS)
        .filter(PQRS.estado == "Nueva", PQRS.comite.is_(None))
        .all()
    )


def obtener_todas(db: Session):
    # Historial completo, de la más reciente a la más antigua
    return db.query(PQRS).order_by(PQRS.created_at.desc()).all()


def obtener_por_id(db: Session, pqrs_id: int):
    return db.query(PQRS).filter(PQRS.id == pqrs_id).first()


def obtener_por_codigo(db: Session, codigo: str):
    return db.query(PQRS).filter(PQRS.codigo_seguimiento == codigo).first()


def obtener_mias(db: Session, usuario_id: int):
    # PQRS que radicó este usuario (las que tienen su FK), más recientes primero.
    return (
        db.query(PQRS)
        .filter(PQRS.radicado_por_id == usuario_id)
        .order_by(PQRS.created_at.desc())
        .all()
    )


def obtener_asignadas(db: Session, comite: str):
    # PQRS asignadas a un comité/comisión concreto, de la más reciente a la más antigua
    return (
        db.query(PQRS)
        .filter(PQRS.comite == comite)
        .order_by(PQRS.created_at.desc())
        .all()
    )
