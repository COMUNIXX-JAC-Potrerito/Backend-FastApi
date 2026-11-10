"""Bitácora de comunicaciones externas (enviadas a / recibidas de otras entidades)."""

from sqlalchemy.orm import Session

from app.core.errores import DatosInvalidos, NoEncontrado
from app.core.tiempo import ahora_utc
from app.models.comunicacion import Comunicacion
from app.schemas.comunicacion import ComunicacionCreate

TIPOS_VALIDOS = ("enviada", "recibida")


def es_tipo_valido(tipo: str) -> bool:
    return tipo in TIPOS_VALIDOS


def registrar(db: Session, datos: ComunicacionCreate, registrado_por_id: int) -> Comunicacion:
    if not es_tipo_valido(datos.tipo):
        raise DatosInvalidos("El tipo debe ser 'enviada' o 'recibida'")
    comunicacion = Comunicacion(
        **datos.model_dump(exclude={"fecha"}),
        fecha=datos.fecha or ahora_utc(),
        registrado_por_id=registrado_por_id,
    )
    db.add(comunicacion)
    db.commit()
    db.refresh(comunicacion)
    return comunicacion


def listar(db: Session, tipo: str | None = None) -> list[Comunicacion]:
    """Comunicaciones (filtradas por tipo si se indica), más recientes primero."""
    query = db.query(Comunicacion)
    if tipo:
        query = query.filter(Comunicacion.tipo == tipo)
    return query.order_by(Comunicacion.fecha.desc(), Comunicacion.id.desc()).all()


def eliminar(db: Session, comunicacion_id: int) -> None:
    comunicacion = db.get(Comunicacion, comunicacion_id)
    if comunicacion is None:
        raise NoEncontrado("Comunicación no encontrada")
    db.delete(comunicacion)
    db.commit()
