from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.publicacion import PublicacionCreate, PublicacionResponse
from app.services.auth.roles import ROLES_GESTION
from app.services.publicaciones.gestion import (
    actualizar_publicacion,
    crear_publicacion,
    eliminar_publicacion,
    listar_publicaciones,
)

router = APIRouter()


# ---------- Público: la comunidad ve las publicaciones (HU14) ----------
@router.get("/publicaciones", response_model=list[PublicacionResponse])
def listar(categoria: str | None = None, db: Session = Depends(get_db)):
    return listar_publicaciones(db, categoria)


# ---------- Protegidos: solo dignatarios publican/editan/borran ----------
@router.post("/publicaciones", response_model=PublicacionResponse, status_code=status.HTTP_201_CREATED)
def crear(
    data: PublicacionCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    try:
        publicacion = crear_publicacion(
            db,
            categoria=data.categoria,
            titulo=data.titulo,
            contenido=data.contenido,
            fecha_evento=data.fecha_evento,
            publicado_por_id=usuario.id,
            adjunto_url=data.adjunto_url,
            adjunto_tipo=data.adjunto_tipo,
            adjunto_nombre=data.adjunto_nombre,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return publicacion


@router.put("/publicaciones/{publicacion_id}", response_model=PublicacionResponse)
def editar(
    publicacion_id: int,
    data: PublicacionCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    try:
        publicacion = actualizar_publicacion(
            db,
            publicacion_id,
            categoria=data.categoria,
            titulo=data.titulo,
            contenido=data.contenido,
            fecha_evento=data.fecha_evento,
            adjunto_url=data.adjunto_url,
            adjunto_tipo=data.adjunto_tipo,
            adjunto_nombre=data.adjunto_nombre,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if publicacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
    return publicacion


@router.delete("/publicaciones/{publicacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(
    publicacion_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    if not eliminar_publicacion(db, publicacion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publicación no encontrada")
