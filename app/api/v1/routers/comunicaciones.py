from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.comunicacion import ComunicacionCreate, ComunicacionResponse
from app.services.auth.roles import ROLES_GESTION
from app.services.comunicaciones.gestion import eliminar, listar, registrar

router = APIRouter()


@router.post("/comunicaciones", response_model=ComunicacionResponse, status_code=status.HTTP_201_CREATED)
def crear(
    data: ComunicacionCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    try:
        return registrar(
            db,
            tipo=data.tipo,
            entidad=data.entidad,
            asunto=data.asunto,
            descripcion=data.descripcion,
            fecha=data.fecha,
            registrado_por_id=usuario.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/comunicaciones", response_model=list[ComunicacionResponse])
def obtener(
    tipo: str | None = None,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    return listar(db, tipo)


@router.delete("/comunicaciones/{comunicacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(
    comunicacion_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    if not eliminar(db, comunicacion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comunicación no encontrada")
