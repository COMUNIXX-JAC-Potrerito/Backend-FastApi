from sqlalchemy.orm import Session

from app.models.pqrs import PQRS
from app.services.pqrs.catalogos import es_tipo_valido


def crear_pqrs(
    db: Session,
    tipo: str,
    asunto: str,
    descripcion: str,
    es_anonima: bool,
    nombre_contacto: str | None,
    email_contacto: str | None,
    telefono_contacto: str | None,
    radicado_por_id: int | None,
) -> PQRS:
    if not es_tipo_valido(tipo):
        raise ValueError("El tipo de PQRS no es válido (Peticion, Queja, Reclamo o Sugerencia)")

    nueva_pqrs = PQRS(
        tipo=tipo,
        asunto=asunto,
        descripcion=descripcion,
        es_anonima=es_anonima,
        nombre_contacto=nombre_contacto,
        email_contacto=email_contacto,
        telefono_contacto=telefono_contacto,
        radicado_por_id=radicado_por_id,
    )

    db.add(nueva_pqrs)
    db.commit()
    db.refresh(nueva_pqrs)

    return nueva_pqrs
