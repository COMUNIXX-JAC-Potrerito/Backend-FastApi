from sqlalchemy.orm import Session

from app.services.pqrs.anonimato import ocultar_si_anonima
from app.services.pqrs.consultas import obtener_entrantes


def listar_entrantes(db: Session):
    pqrs_entrantes = obtener_entrantes(db)
    return [ocultar_si_anonima(pqrs) for pqrs in pqrs_entrantes]
