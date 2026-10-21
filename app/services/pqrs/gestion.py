from sqlalchemy.orm import Session

from app.services.pqrs.anonimato import ocultar_si_anonima
from app.services.pqrs.catalogos import (
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


def responder_pqrs(db: Session, pqrs_id: int, respuesta: str):
    """Guarda la respuesta de la JAC y su fecha; None si la PQRS no existe."""
    from datetime import datetime

    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None
    pqrs.respuesta = respuesta
    pqrs.respuesta_fecha = datetime.utcnow()
    db.commit()
    db.refresh(pqrs)
    return pqrs


def asignar_comite(db: Session, pqrs_id: int, comite: str):
    """Asigna un comité a la PQRS (valida el comité; NO cambia el estado)."""
    if not es_comite_valido(comite):
        raise ValueError("El comité/cargo indicado no es válido")

    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None

    pqrs.comite = comite
    # No se cambia el estado: la PQRS sigue "Nueva" para el comité hasta que
    # el dignatario la mueva a En_Proceso/Finalizada desde "Mis asignadas".
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
