"""Gestión de PQRS por parte de los dignatarios."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.errores import DatosInvalidos, NoEncontrado, SinPermiso
from app.core.tiempo import ahora_utc
from app.models.pqrs import PQRS, RespuestaPQRS
from app.services.pqrs.anonimato import ocultar_si_anonima
from app.services.pqrs.catalogos import (
    ESTADO_EN_PROCESO,
    ESTADO_FINALIZADA,
    ESTADOS_VALIDOS,
    es_comite_valido,
    es_estado_valido,
)
from app.services.pqrs.consultas import (
    obtener_asignadas,
    obtener_entrantes,
    obtener_mias,
    obtener_por_id,
    obtener_todas,
)

# Tiempo máximo para editar una respuesta ya enviada.
VENTANA_EDICION = timedelta(minutes=5)


def listar_entrantes(db: Session) -> list[dict]:
    return [ocultar_si_anonima(pqrs) for pqrs in obtener_entrantes(db)]


def listar_historial(db: Session) -> list[dict]:
    return [ocultar_si_anonima(pqrs) for pqrs in obtener_todas(db)]


def listar_asignadas(db: Session, comite: str | None) -> list[dict]:
    """PQRS de la comisión del dignatario (vacío si no tiene comisión)."""
    if not comite:
        return []
    return [ocultar_si_anonima(pqrs) for pqrs in obtener_asignadas(db, comite)]


def listar_mias(db: Session, usuario_id: int) -> list[PQRS]:
    """PQRS del propio usuario, completas (son suyas)."""
    return obtener_mias(db, usuario_id)


def _guardar(db: Session, pqrs: PQRS) -> dict:
    db.commit()
    db.refresh(pqrs)
    return ocultar_si_anonima(pqrs)


def agregar_respuesta(db: Session, pqrs_id: int, texto: str, autor_id: int) -> dict:
    """Agrega una respuesta al hilo y pasa la PQRS a En_Proceso (no reabre finalizadas)."""
    pqrs = obtener_por_id(db, pqrs_id)
    pqrs.respuestas.append(RespuestaPQRS(texto=texto, autor_id=autor_id))
    if pqrs.estado != ESTADO_FINALIZADA:
        pqrs.estado = ESTADO_EN_PROCESO
    return _guardar(db, pqrs)


def editar_respuesta(db: Session, respuesta_id: int, texto: str, autor_id: int) -> dict:
    """Edita una respuesta propia dentro de los 5 minutos siguientes a su envío."""
    respuesta = db.get(RespuestaPQRS, respuesta_id)
    if respuesta is None:
        raise NoEncontrado("No existe la respuesta indicada")
    if respuesta.autor_id != autor_id:
        raise SinPermiso("Solo el autor puede editar esta respuesta")
    if ahora_utc() - respuesta.created_at > VENTANA_EDICION:
        raise DatosInvalidos("Ya no se puede editar esta respuesta (pasaron más de 5 minutos)")
    respuesta.texto = texto
    return _guardar(db, respuesta.pqrs)


def asignar_comite(db: Session, pqrs_id: int, comite: str) -> dict:
    """Asigna el comité responsable. El estado no cambia: sigue "Nueva" para el comité."""
    if not es_comite_valido(comite):
        raise DatosInvalidos("El comité/cargo indicado no es válido")
    pqrs = obtener_por_id(db, pqrs_id)
    pqrs.comite = comite
    return _guardar(db, pqrs)


def cambiar_estado(db: Session, pqrs_id: int, estado: str) -> dict:
    if not es_estado_valido(estado):
        raise DatosInvalidos(f"El estado indicado no es válido ({', '.join(ESTADOS_VALIDOS)})")
    pqrs = obtener_por_id(db, pqrs_id)
    pqrs.estado = estado
    return _guardar(db, pqrs)
