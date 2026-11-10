"""Publicaciones: la comunidad las consulta y los dignatarios las gestionan."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import solo_dignatarios
from app.db.session import get_db
from app.models.user import User
from app.schemas.publicacion import PublicacionCreate, PublicacionResponse
from app.services.publicaciones import gestion

router = APIRouter(tags=["publicaciones"])


@router.get("/publicaciones", response_model=list[PublicacionResponse])
def listar(categoria: str | None = None, db: Session = Depends(get_db)):
    """Publicaciones para la comunidad (filtrando por categoría si se indica)."""
    return gestion.listar_publicaciones(db, categoria)


@router.post("/publicaciones", response_model=PublicacionResponse, status_code=status.HTTP_201_CREATED)
def crear(data: PublicacionCreate, db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    return gestion.crear_publicacion(db, data, usuario.id)


@router.put(
    "/publicaciones/{publicacion_id}",
    response_model=PublicacionResponse,
    dependencies=[Depends(solo_dignatarios)],
)
def editar(publicacion_id: int, data: PublicacionCreate, db: Session = Depends(get_db)):
    return gestion.actualizar_publicacion(db, publicacion_id, data)


@router.delete(
    "/publicaciones/{publicacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(solo_dignatarios)],
)
def borrar(publicacion_id: int, db: Session = Depends(get_db)):
    gestion.eliminar_publicacion(db, publicacion_id)
