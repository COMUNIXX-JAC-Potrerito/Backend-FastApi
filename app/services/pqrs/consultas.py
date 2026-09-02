from sqlalchemy.orm import Session

from app.models.pqrs import PQRS


def obtener_entrantes(db: Session):
    # "Entrantes" = las solicitudes nuevas que aún no han sido atendidas
    return db.query(PQRS).filter(PQRS.estado == "Nueva").all()
