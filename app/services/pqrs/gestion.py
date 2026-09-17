from sqlalchemy.orm import Session

from app.services.pqrs.anonimato import ocultar_si_anonima
from app.services.pqrs.catalogos import (
    ESTADO_EN_PROCESO,
    es_comite_valido,
    es_estado_valido,
)
from app.services.pqrs.consultas import (
    obtener_asignadas,
    obtener_entrantes,
    obtener_por_id,
    obtener_todas,
)


def listar_entrantes(db: Session):
    pqrs_entrantes = obtener_entrantes(db)
    return [ocultar_si_anonima(pqrs) for pqrs in pqrs_entrantes]


def listar_historial(db: Session):
    todas = obtener_todas(db)
    return [ocultar_si_anonima(pqrs) for pqrs in todas]


def listar_asignadas(db: Session, comite: str):
    asignadas = obtener_asignadas(db, comite)
    return [ocultar_si_anonima(pqrs) for pqrs in asignadas]


def responder_pqrs(db: Session, pqrs_id: int, respuesta: str):
    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None
    pqrs.respuesta = respuesta
    db.commit()
    db.refresh(pqrs)
    return pqrs


def asignar_comite(db: Session, pqrs_id: int, comite: str):
    if not es_comite_valido(comite):
        raise ValueError("El comité/cargo indicado no es válido")

    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None

    pqrs.comite = comite
    pqrs.estado = ESTADO_EN_PROCESO  # al asignarse a un comité, pasa a estar en proceso
    db.commit()
    db.refresh(pqrs)
    return pqrs


def cambiar_estado(db: Session, pqrs_id: int, estado: str):
    if not es_estado_valido(estado):
        raise ValueError("El estado indicado no es válido (Nueva, En_Proceso o Finalizada)")

    pqrs = obtener_por_id(db, pqrs_id)
    if pqrs is None:
        return None

    pqrs.estado = estado
    db.commit()
    db.refresh(pqrs)
    return pqrs
