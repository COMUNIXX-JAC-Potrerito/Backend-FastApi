from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.pqrs import (
    AsignarComite,
    CambiarEstado,
    PQRSCreate,
    PQRSResponse,
    PQRSSeguimiento,
    ResponderPQRS,
)
from app.services.auth.roles import ROLES_GESTION
from app.services.pqrs.anonimato import ocultar_si_anonima
from app.services.pqrs.gestion import (
    asignar_comite,
    cambiar_estado,
    listar_asignadas,
    listar_entrantes,
    listar_historial,
    responder_pqrs,
)
from app.services.pqrs.radicacion import crear_pqrs
from app.services.pqrs.seguimiento import consultar_por_codigo

router = APIRouter()


# ---------- Público: radicar una PQRS ----------
@router.post("/pqrs", response_model=PQRSResponse, status_code=status.HTTP_201_CREATED)
def radicar_pqrs(
    data: PQRSCreate,
    db: Session = Depends(get_db),
    usuario: User | None = Depends(get_current_user_optional),
):
    # Si viene logueado, se asocia su id; si no (turista), queda sin FK.
    radicado_por_id = usuario.id if usuario is not None else None
    try:
        pqrs = crear_pqrs(
            db,
            tipo=data.tipo,
            asunto=data.asunto,
            descripcion=data.descripcion,
            es_anonima=data.es_anonima,
            nombre_contacto=data.nombre_contacto,
            email_contacto=data.email_contacto,
            telefono_contacto=data.telefono_contacto,
            radicado_por_id=radicado_por_id,
            adjunto_url=data.adjunto_url,
            adjunto_tipo=data.adjunto_tipo,
            adjunto_nombre=data.adjunto_nombre,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    # El radicador SÍ ve su propio código de seguimiento (no se oculta nada).
    return pqrs


# ---------- Público: consultar el estado por código ----------
@router.get("/pqrs/seguimiento/{codigo}", response_model=PQRSSeguimiento)
def seguimiento_pqrs(codigo: str, db: Session = Depends(get_db)):
    pqrs = consultar_por_codigo(db, codigo)
    if pqrs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe una PQRS con ese código de seguimiento",
        )
    return pqrs


# ---------- Protegidos (solo miembros de la JAC autenticados) ----------
@router.get("/pqrs/entrantes", response_model=list[PQRSResponse])
def pqrs_entrantes(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    return listar_entrantes(db)


@router.get("/pqrs/historial", response_model=list[PQRSResponse])
def pqrs_historial(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    return listar_historial(db)


@router.get("/pqrs/asignadas", response_model=list[PQRSResponse])
def pqrs_asignadas(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    # PQRS asignadas a la comisión del dignatario. Si no tiene comisión, lista vacía.
    if not usuario.comite:
        return []
    return listar_asignadas(db, usuario.comite)


@router.put("/pqrs/{pqrs_id}/responder", response_model=PQRSResponse)
def responder(
    pqrs_id: int,
    data: ResponderPQRS,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    pqrs = responder_pqrs(db, pqrs_id, data.respuesta)
    if pqrs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No existe la PQRS indicada"
        )
    return ocultar_si_anonima(pqrs)


@router.put("/pqrs/{pqrs_id}/asignar", response_model=PQRSResponse)
def asignar(
    pqrs_id: int,
    data: AsignarComite,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    try:
        pqrs = asignar_comite(db, pqrs_id, data.comite)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if pqrs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No existe la PQRS indicada"
        )
    return ocultar_si_anonima(pqrs)


@router.put("/pqrs/{pqrs_id}/estado", response_model=PQRSResponse)
def actualizar_estado(
    pqrs_id: int,
    data: CambiarEstado,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    try:
        pqrs = cambiar_estado(db, pqrs_id, data.estado)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if pqrs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No existe la PQRS indicada"
        )
    return ocultar_si_anonima(pqrs)
