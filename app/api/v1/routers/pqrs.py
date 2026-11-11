"""PQRS: radicación pública, seguimiento por código y gestión por dignatarios."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional, solo_dignatarios
from app.core.limites import limite_radicar_pqrs, limite_seguimiento
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
from app.services.pqrs import gestion
from app.services.pqrs.radicacion import completar_contacto, crear_pqrs
from app.services.pqrs.seguimiento import consultar_por_codigo

router = APIRouter(tags=["pqrs"])


# ---------- Público ----------
@router.post(
    "/pqrs",
    response_model=PQRSResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limite_radicar_pqrs)],
)
def radicar_pqrs(
    data: PQRSCreate,
    db: Session = Depends(get_db),
    usuario: User | None = Depends(get_current_user_optional),
):
    """Radica una PQRS. Con sesión se asocia al usuario y completa su contacto."""
    radicado_por_id = usuario.id if usuario else None
    # Quien radica sí ve su propio código y sus datos.
    return crear_pqrs(db, completar_contacto(data, usuario), radicado_por_id)


@router.get(
    "/pqrs/seguimiento/{codigo}",
    response_model=PQRSSeguimiento,
    dependencies=[Depends(limite_seguimiento)],
)
def seguimiento_pqrs(codigo: str, db: Session = Depends(get_db)):
    """Estado de una PQRS por su código (sin datos de identidad)."""
    return consultar_por_codigo(db, codigo)


# ---------- Con sesión ----------
@router.get("/pqrs/mias", response_model=list[PQRSResponse])
def pqrs_mias(db: Session = Depends(get_db), usuario: User = Depends(get_current_user)):
    """PQRS que radicó el usuario logueado."""
    return gestion.listar_mias(db, usuario.id)


# ---------- Dignatarios ----------
@router.get("/pqrs/entrantes", response_model=list[PQRSResponse], dependencies=[Depends(solo_dignatarios)])
def pqrs_entrantes(db: Session = Depends(get_db)):
    """PQRS nuevas sin comité asignado."""
    return gestion.listar_entrantes(db)


@router.get("/pqrs/historial", response_model=list[PQRSResponse], dependencies=[Depends(solo_dignatarios)])
def pqrs_historial(db: Session = Depends(get_db)):
    """Todas las PQRS, con el anonimato aplicado."""
    return gestion.listar_historial(db)


@router.get("/pqrs/asignadas", response_model=list[PQRSResponse])
def pqrs_asignadas(db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    """PQRS de la comisión del dignatario (vacío si no tiene comisión)."""
    return gestion.listar_asignadas(db, usuario.comite)


@router.put("/pqrs/{pqrs_id}/responder", response_model=PQRSResponse)
def responder(
    pqrs_id: int,
    data: ResponderPQRS,
    db: Session = Depends(get_db),
    usuario: User = Depends(solo_dignatarios),
):
    """Agrega una respuesta al hilo y pasa la PQRS a En_Proceso."""
    return gestion.agregar_respuesta(db, pqrs_id, data.respuesta, usuario.id)


@router.put("/pqrs/respuestas/{respuesta_id}", response_model=PQRSResponse)
def editar_una_respuesta(
    respuesta_id: int,
    data: ResponderPQRS,
    db: Session = Depends(get_db),
    usuario: User = Depends(solo_dignatarios),
):
    """Edita una respuesta propia dentro de los 5 minutos siguientes a su envío."""
    return gestion.editar_respuesta(db, respuesta_id, data.respuesta, usuario.id)


@router.put("/pqrs/{pqrs_id}/asignar", response_model=PQRSResponse)
def asignar(
    pqrs_id: int,
    data: AsignarComite,
    db: Session = Depends(get_db),
    usuario: User = Depends(solo_dignatarios),
):
    """Asigna el comité responsable (RN-012: no se reasigna salvo un superadministrador)."""
    return gestion.asignar_comite(db, pqrs_id, data.comite, usuario.role)


@router.put("/pqrs/{pqrs_id}/estado", response_model=PQRSResponse, dependencies=[Depends(solo_dignatarios)])
def actualizar_estado(pqrs_id: int, data: CambiarEstado, db: Session = Depends(get_db)):
    """Cambia el estado (Nueva, En_Proceso, En_Espera o Finalizada)."""
    return gestion.cambiar_estado(db, pqrs_id, data.estado)
