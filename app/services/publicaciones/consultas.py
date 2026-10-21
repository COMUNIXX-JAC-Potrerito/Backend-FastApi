from sqlalchemy.orm import Session

from app.models.publicacion import Publicacion


def obtener_todas(db: Session, categoria: str | None = None):
    """Devuelve las publicaciones (filtradas por categoría si se indica), más recientes primero."""
    query = db.query(Publicacion)
    if categoria:
        query = query.filter(Publicacion.categoria == categoria)
    return query.order_by(Publicacion.created_at.desc()).all()


def obtener_por_id(db: Session, publicacion_id: int):
    """Busca una publicación por su id; devuelve None si no existe."""
    return db.query(Publicacion).filter(Publicacion.id == publicacion_id).first()
