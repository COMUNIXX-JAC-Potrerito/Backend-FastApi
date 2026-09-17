from sqlalchemy.orm import Session

from app.models.publicacion import Publicacion


def obtener_todas(db: Session, categoria: str | None = None):
    query = db.query(Publicacion)
    if categoria:
        query = query.filter(Publicacion.categoria == categoria)
    return query.order_by(Publicacion.created_at.desc()).all()


def obtener_por_id(db: Session, publicacion_id: int):
    return db.query(Publicacion).filter(Publicacion.id == publicacion_id).first()
