from datetime import datetime

from sqlalchemy.orm import Session

from app.models.comunicacion import Comunicacion

TIPOS_VALIDOS = ["enviada", "recibida"]


def es_tipo_valido(tipo: str) -> bool:
    """Indica si el tipo de comunicación es válido ('enviada' o 'recibida')."""
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
    """Crea y guarda una comunicación externa en la bitácora (valida el tipo)."""
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
    """Devuelve las comunicaciones (filtradas por tipo si se indica), más recientes primero."""
    query = db.query(Comunicacion)
    if tipo:
        query = query.filter(Comunicacion.tipo == tipo)
    return query.order_by(Comunicacion.fecha.desc()).all()


def eliminar(db: Session, comunicacion_id: int) -> bool:
    """Borra una comunicación por id; devuelve True si existía y False si no."""
    comunicacion = db.query(Comunicacion).filter(Comunicacion.id == comunicacion_id).first()
    if comunicacion is None:
        return False
    db.delete(comunicacion)
    db.commit()
    return True
