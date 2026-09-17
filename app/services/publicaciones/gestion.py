from datetime import datetime

from sqlalchemy.orm import Session

from app.models.publicacion import Publicacion
from app.services.publicaciones.catalogos import es_categoria_valida
from app.services.publicaciones.consultas import obtener_por_id, obtener_todas


def listar_publicaciones(db: Session, categoria: str | None = None):
    return obtener_todas(db, categoria)


def crear_publicacion(
    db: Session,
    categoria: str,
    titulo: str,
    contenido: str,
    fecha_evento: datetime | None,
    publicado_por_id: int | None,
) -> Publicacion:
    if not es_categoria_valida(categoria):
        raise ValueError("La categoría no es válida (decision, actividad o contenido)")

    publicacion = Publicacion(
        categoria=categoria,
        titulo=titulo,
        contenido=contenido,
        fecha_evento=fecha_evento,
        publicado_por_id=publicado_por_id,
    )
    db.add(publicacion)
    db.commit()
    db.refresh(publicacion)
    return publicacion


def actualizar_publicacion(
    db: Session,
    publicacion_id: int,
    categoria: str,
    titulo: str,
    contenido: str,
    fecha_evento: datetime | None,
):
    if not es_categoria_valida(categoria):
        raise ValueError("La categoría no es válida (decision, actividad o contenido)")

    publicacion = obtener_por_id(db, publicacion_id)
    if publicacion is None:
        return None

    publicacion.categoria = categoria
    publicacion.titulo = titulo
    publicacion.contenido = contenido
    publicacion.fecha_evento = fecha_evento
    db.commit()
    db.refresh(publicacion)
    return publicacion


def eliminar_publicacion(db: Session, publicacion_id: int) -> bool:
    publicacion = obtener_por_id(db, publicacion_id)
    if publicacion is None:
        return False
    db.delete(publicacion)
    db.commit()
    return True
