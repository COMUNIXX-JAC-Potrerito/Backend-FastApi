"""Encuestas y censos: respuesta pública y gestión por dignatarios."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional, solo_dignatarios
from app.core.limites import limite_responder_encuesta
from app.db.session import get_db
from app.models.user import User
from app.schemas.encuesta import (
    EncuestaCreate,
    EncuestaDetalle,
    EncuestaResultados,
    EncuestaResumen,
    ParticipanteResponse,
    PublicarEncuesta,
    ResponderEncuesta,
)
from app.services.auth.roles import es_dignatario
from app.services.encuestas import gestion, respuestas

router = APIRouter(tags=["encuestas"])


# ---------- Público ----------
@router.get("/encuestas", response_model=list[EncuestaResumen])
def listar_publicas(db: Session = Depends(get_db)):
    """Encuestas publicadas."""
    return gestion.listar_encuestas(db, solo_publicadas=True)


@router.get(
    "/encuestas/gestion",
    response_model=list[EncuestaResumen],
    dependencies=[Depends(solo_dignatarios)],
)
def listar_gestion(db: Session = Depends(get_db)):
    """Todas las encuestas, incluidos los borradores."""
    return gestion.listar_encuestas(db, solo_publicadas=False)


@router.get("/encuestas/mis-respuestas", response_model=list[int])
def mis_respuestas(db: Session = Depends(get_db), usuario: User = Depends(get_current_user)):
    """IDs de las encuestas que el usuario ya respondió."""
    return respuestas.encuestas_respondidas_por(db, usuario.id)


@router.get("/encuestas/{encuesta_id}", response_model=EncuestaDetalle)
def detalle(
    encuesta_id: int,
    db: Session = Depends(get_db),
    usuario: User | None = Depends(get_current_user_optional),
):
    """Encuesta con sus preguntas (las no publicadas solo las ven dignatarios)."""
    return gestion.obtener_visible(db, encuesta_id, es_dignatario(usuario.role if usuario else None))


@router.post(
    "/encuestas/{encuesta_id}/responder",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limite_responder_encuesta)],
)
def responder(
    encuesta_id: int,
    data: ResponderEncuesta,
    db: Session = Depends(get_db),
    usuario: User | None = Depends(get_current_user_optional),
):
    """Registra una respuesta (con sesión se usan los datos de la cuenta)."""
    participante = respuestas.participante_desde(data, usuario)
    respuestas.responder_encuesta(db, encuesta_id, data.items, participante)
    return {"ok": True}


# ---------- Dignatarios ----------
@router.post("/encuestas", response_model=EncuestaDetalle, status_code=status.HTTP_201_CREATED)
def crear(data: EncuestaCreate, db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    """Crea una encuesta o censo con sus preguntas."""
    return gestion.crear_encuesta(db, data, usuario.id)


@router.put(
    "/encuestas/{encuesta_id}/publicar",
    response_model=EncuestaResumen,
    dependencies=[Depends(solo_dignatarios)],
)
def publicar(encuesta_id: int, data: PublicarEncuesta, db: Session = Depends(get_db)):
    """Publica o despublica una encuesta."""
    return gestion.publicar_encuesta(db, encuesta_id, data.publicada)


@router.delete(
    "/encuestas/{encuesta_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(solo_dignatarios)],
)
def borrar(encuesta_id: int, db: Session = Depends(get_db)):
    """Elimina una encuesta y sus respuestas."""
    gestion.eliminar_encuesta(db, encuesta_id)


@router.get(
    "/encuestas/{encuesta_id}/resultados",
    response_model=EncuestaResultados,
    dependencies=[Depends(solo_dignatarios)],
)
def ver_resultados(encuesta_id: int, db: Session = Depends(get_db)):
    """Resultados agregados por pregunta."""
    return respuestas.resultados(db, encuesta_id)


@router.get(
    "/encuestas/{encuesta_id}/participantes",
    response_model=list[ParticipanteResponse],
    dependencies=[Depends(solo_dignatarios)],
)
def ver_participantes(encuesta_id: int, db: Session = Depends(get_db)):
    """Personas que respondieron la encuesta."""
    return respuestas.participantes(db, encuesta_id)
