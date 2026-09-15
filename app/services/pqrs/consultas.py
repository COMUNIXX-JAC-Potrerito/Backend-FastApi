from sqlalchemy.orm import Session

from app.models.pqrs import PQRS


def obtener_entrantes(db: Session):
    # "Entrantes" = las solicitudes nuevas que aún no han sido atendidas
    return db.query(PQRS).filter(PQRS.estado == "Nueva").all()


def obtener_todas(db: Session):
    # Historial completo, de la más reciente a la más antigua
    return db.query(PQRS).order_by(PQRS.created_at.desc()).all()


def obtener_por_id(db: Session, pqrs_id: int):
    return db.query(PQRS).filter(PQRS.id == pqrs_id).first()


def obtener_por_codigo(db: Session, codigo: str):
    return db.query(PQRS).filter(PQRS.codigo_seguimiento == codigo).first()
