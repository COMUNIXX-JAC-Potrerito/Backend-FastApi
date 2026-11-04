from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.pqrs import RespuestaPQRS
from app.services.pqrs.anonimato import ocultar_si_anonima
from app.services.pqrs.catalogos import (
    ESTADO_EN_PROCESO,
    ESTADO_FINALIZADA,
    es_comite_valido,
    es_estado_valido,
)

# Tiempo máximo para editar una respuesta ya enviada.
VENTANA_EDICION = timedelta(minutes=5)
from app.services.pqrs.consultas import (
    obtener_asignadas,
    obtener_entrantes,
    obtener_mias,
    obtener_por_id,
    obtener_todas,
)


def listar_entrantes(db: Session):
    """Lista las PQRS entrantes aplicando el anonimato (oculta identidad)."""
    pqrs_entrantes = obtener_entrantes(db)
    return [ocultar_si_anonima(pqrs) for pqrs in pqrs_entrantes]


def listar_historial(db: Session):
    """Lista todas las PQRS (historial) aplicando el anonimato."""
    todas = obtener_todas(db)
    return [ocultar_si_anonima(pqrs) for pqrs in todas]


def listar_asignadas(db: Session, comite: str):
    """Lista las PQRS de un comité aplicando el anonimato."""
    asignadas = obtener_asignadas(db, comite)
    return [ocultar_si_anonima(pqrs) for pqrs in asignadas]


def listar_mias(db: Session, usuario_id: int):
    """Lista las PQRS del propio usuario (completas, sin ocultar; son suyas)."""
    return obtener_mias(db, usuario_id)


def agregar_respuesta(db: Session, pqrs_id: int, texto: str, autor_id: int | None):
    """Agrega una respuesta de la JAC a la PQRS (permite varias por PQRS).

    Al responder, la PQRS pasa a "En_Proceso" (salvo que ya esté "Finalizada",
    que no se reabre). Devuelve la PQRS; None si no existe.
    """
    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None
    db.add(RespuestaPQRS(pqrs_id=pqrs_id, texto=texto, autor_id=autor_id))
    # Responder avanza el estado a "En_Proceso" (no revive una ya finalizada).
    if pqrs.estado != ESTADO_FINALIZADA:
        pqrs.estado = ESTADO_EN_PROCESO
    db.commit()
    db.refresh(pqrs)
    return pqrs


def editar_respuesta(db: Session, respuesta_id: int, texto: str):
    """Edita el texto de una respuesta dentro de los 5 min de creada.

    Devuelve (pqrs, error): error="no_existe" o "fuera_de_tiempo"; None sin error.
    """
    respuesta = (
        db.query(RespuestaPQRS).filter(RespuestaPQRS.id == respuesta_id).first()
    )
    if respuesta is None:
        return None, "no_existe"
    if datetime.utcnow() - respuesta.created_at > VENTANA_EDICION:
        return None, "fuera_de_tiempo"
    respuesta.texto = texto
    db.commit()
    pqrs = obtener_por_id(db, respuesta.pqrs_id)
    db.refresh(pqrs)
    return pqrs, None


def asignar_comite(db: Session, pqrs_id: int, comite: str):
    """Asigna un comité a la PQRS. NO cambia el estado: sigue "Nueva" para el comité.

    Se separa la asignación (responsable) del estado (ciclo de vida), como en
    las mesas de ayuda. Al asignar, la PQRS sale de "Entrantes" (ya tiene
    comité) y aparece en "Mis asignadas / Nuevas" del comité, que luego la
    mueve a En_Proceso y Finalizada.
    """
    if not es_comite_valido(comite):
        raise ValueError("El comité/cargo indicado no es válido")

    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None

    pqrs.comite = comite
    # El estado NO se toca: queda "Nueva" (por atender) para el comité.
    db.commit()
    db.refresh(pqrs)
    return pqrs


def cambiar_estado(db: Session, pqrs_id: int, estado: str):
    """Cambia el estado de la PQRS (valida que sea Nueva/En_Proceso/Finalizada)."""
    if not es_estado_valido(estado):
        raise ValueError("El estado indicado no es válido (Nueva, En_Proceso o Finalizada)")

    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None

    pqrs.estado = estado
    db.commit()
    db.refresh(pqrs)
    return pqrs
