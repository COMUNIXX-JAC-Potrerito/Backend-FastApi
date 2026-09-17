from datetime import datetime

from sqlalchemy.orm import Session

from app.models.comunicacion import Comunicacion

TIPOS_VALIDOS = ["enviada", "recibida"]


def es_tipo_valido(tipo: str) -> bool:
    return tipo in TIPOS_VALIDOS


def registrar(
    db: Session,
    tipo: str,
    entidad: str,
    asunto: str,
    descripcion: str | None,
    fecha: datetime | None,
    registrado_por_id: int | None,
):
    if not es_tipo_valido(tipo):
        raise ValueError("El tipo debe ser 'enviada' o 'recibida'")

    comunicacion = Comunicacion(
        tipo=tipo,
        entidad=entidad,
        asunto=asunto,
        descripcion=descripcion,
        fecha=fecha or datetime.utcnow(),
        registrado_por_id=registrado_por_id,
    )
    db.add(comunicacion)
    db.commit()
    db.refresh(comunicacion)
    return comunicacion


def listar(db: Session, tipo: str | None = None):
    query = db.query(Comunicacion)
    if tipo:
        query = query.filter(Comunicacion.tipo == tipo)
    return query.order_by(Comunicacion.fecha.desc()).all()


def eliminar(db: Session, comunicacion_id: int) -> bool:
    comunicacion = db.query(Comunicacion).filter(Comunicacion.id == comunicacion_id).first()
    if comunicacion is None:
        return False
    db.delete(comunicacion)
    db.commit()
    return True
