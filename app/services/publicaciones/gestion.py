"""Publicaciones institucionales: decisiones, actividades y contenidos."""

from sqlalchemy.orm import Session

from app.core.errores import DatosInvalidos, NoEncontrado
from app.models.publicacion import Publicacion
from app.schemas.publicacion import PublicacionCreate
from app.services.publicaciones.catalogos import es_categoria_valida


def _validar(datos: PublicacionCreate) -> None:
    if not es_categoria_valida(datos.categoria):
        raise DatosInvalidos("La categoría no es válida (decision, actividad o contenido)")


def _obtener(db: Session, publicacion_id: int) -> Publicacion:
    publicacion = db.get(Publicacion, publicacion_id)
    if publicacion is None:
        raise NoEncontrado("Publicación no encontrada")
    return publicacion


def listar_publicaciones(db: Session, categoria: str | None = None) -> list[Publicacion]:
    """Publicaciones (filtradas por categoría si se indica), más recientes primero."""
    query = db.query(Publicacion)
    if categoria:
        query = query.filter(Publicacion.categoria == categoria)
    return query.order_by(Publicacion.created_at.desc(), Publicacion.id.desc()).all()


def crear_publicacion(db: Session, datos: PublicacionCreate, publicado_por_id: int) -> Publicacion:
    _validar(datos)
    publicacion = Publicacion(**datos.model_dump(), publicado_por_id=publicado_por_id)
    db.add(publicacion)
    db.commit()
    db.refresh(publicacion)
    return publicacion


def actualizar_publicacion(db: Session, publicacion_id: int, datos: PublicacionCreate) -> Publicacion:
    _validar(datos)
    publicacion = _obtener(db, publicacion_id)
    for campo, valor in datos.model_dump().items():
        setattr(publicacion, campo, valor)
    db.commit()
    db.refresh(publicacion)
    return publicacion


def eliminar_publicacion(db: Session, publicacion_id: int) -> None:
    db.delete(_obtener(db, publicacion_id))
    db.commit()
