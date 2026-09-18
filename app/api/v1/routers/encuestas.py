from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.encuesta import (
    EncuestaCreate,
    EncuestaDetalle,
    EncuestaResultados,
    EncuestaResumen,
    PublicarEncuesta,
    ResponderEncuesta,
)
from app.services.auth.roles import ROLES_GESTION
from app.services.encuestas.gestion import (
    crear_encuesta,
    eliminar_encuesta,
    listar_encuestas,
    obtener_encuesta,
    obtener_preguntas,
    opciones_a_lista,
    publicar_encuesta,
)
from app.services.encuestas.respuestas import responder_encuesta, resultados

router = APIRouter()


def _detalle(encuesta, preguntas) -> dict:
    return {
        "id": encuesta.id,
        "titulo": encuesta.titulo,
        "descripcion": encuesta.descripcion,
        "tipo": encuesta.tipo,
        "publicada": encuesta.publicada,
        "created_at": encuesta.created_at,
        "preguntas": [
            {
                "id": p.id,
                "texto": p.texto,
                "tipo": p.tipo,
                "opciones": opciones_a_lista(p.opciones),
                "orden": p.orden,
            }
            for p in preguntas
        ],
    }


# ---------- Público: encuestas publicadas ----------
@router.get("/encuestas", response_model=list[EncuestaResumen])
def listar_publicas(db: Session = Depends(get_db)):
    return listar_encuestas(db, solo_publicadas=True)


# ---------- Dignatarios: todas (incluye borradores) ----------
@router.get("/encuestas/gestion", response_model=list[EncuestaResumen])
def listar_gestion(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    return listar_encuestas(db, solo_publicadas=False)


@router.get("/encuestas/{encuesta_id}", response_model=EncuestaDetalle)
def detalle(
    encuesta_id: int,
    db: Session = Depends(get_db),
    usuario: User | None = Depends(get_current_user_optional),
):
    encuesta = obtener_encuesta(db, encuesta_id)
    if encuesta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    es_dignatario = usuario is not None and usuario.role in ROLES_GESTION
    if not encuesta.publicada and not es_dignatario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return _detalle(encuesta, obtener_preguntas(db, encuesta_id))


@router.post("/encuestas", response_model=EncuestaDetalle, status_code=status.HTTP_201_CREATED)
def crear(
    data: EncuestaCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    try:
        encuesta = crear_encuesta(
            db, data.titulo, data.descripcion, data.tipo, data.preguntas, usuario.id
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return _detalle(encuesta, obtener_preguntas(db, encuesta.id))


@router.put("/encuestas/{encuesta_id}/publicar", response_model=EncuestaResumen)
def publicar(
    encuesta_id: int,
    data: PublicarEncuesta,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    encuesta = publicar_encuesta(db, encuesta_id, data.publicada)
    if encuesta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return encuesta


@router.delete("/encuestas/{encuesta_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(
    encuesta_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    if not eliminar_encuesta(db, encuesta_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")


# ---------- Público: responder ----------
@router.post("/encuestas/{encuesta_id}/responder", status_code=status.HTTP_201_CREATED)
def responder(
    encuesta_id: int,
    data: ResponderEncuesta,
    db: Session = Depends(get_db),
    usuario: User | None = Depends(get_current_user_optional),
):
    # Si viene logueado, se usan los datos de su cuenta.
    if usuario is not None:
        nombre = data.nombre or usuario.full_name
        email = data.email or usuario.email
        telefono = data.telefono or usuario.phone
    else:
        nombre, email, telefono = data.nombre, data.email, data.telefono

    _, error = responder_encuesta(
        db,
        encuesta_id,
        data.items,
        usuario.id if usuario is not None else None,
        nombre,
        email,
        telefono,
    )
    if error == "no_existe":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    if error == "no_publicada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La encuesta no está publicada"
        )
    if error == "datos_incompletos":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Indica tu nombre y un correo o teléfono para responder",
        )
    return {"ok": True}


# ---------- Dignatarios: resultados ----------
@router.get("/encuestas/{encuesta_id}/resultados", response_model=EncuestaResultados)
def ver_resultados(
    encuesta_id: int,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    datos = resultados(db, encuesta_id)
    if datos is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return datos
