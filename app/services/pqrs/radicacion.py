"""Radicación de PQRS por parte de la comunidad."""

from sqlalchemy.orm import Session

from app.core.errores import DatosInvalidos
from app.models.pqrs import PQRS
from app.models.user import User
from app.schemas.pqrs import PQRSCreate
from app.services.pqrs.catalogos import es_tipo_valido


def _tiene_texto(valor: str | None) -> bool:
    return bool(valor and valor.strip())


def completar_contacto(datos: PQRSCreate, usuario: User | None) -> PQRSCreate:
    """Si hay sesión y la PQRS no es anónima, completa el contacto con la cuenta."""
    if usuario is None or datos.es_anonima:
        return datos
    return datos.model_copy(
        update={
            "nombre_contacto": datos.nombre_contacto or usuario.full_name,
            "email_contacto": datos.email_contacto or usuario.email,
            "telefono_contacto": datos.telefono_contacto or usuario.phone,
        }
    )


def _validar(datos: PQRSCreate) -> None:
    if not es_tipo_valido(datos.tipo):
        raise DatosInvalidos("El tipo de PQRS no es válido (Peticion, Queja, Reclamo o Sugerencia)")
    if datos.es_anonima:
        return
    if not _tiene_texto(datos.nombre_contacto):
        raise DatosInvalidos("Indica tu nombre, o marca la PQRS como anónima")
    if not (_tiene_texto(datos.email_contacto) or _tiene_texto(datos.telefono_contacto)):
        raise DatosInvalidos("Indica un correo o un teléfono de contacto, o marca la PQRS como anónima")


def crear_pqrs(db: Session, datos: PQRSCreate, radicado_por_id: int | None) -> PQRS:
    """Valida y guarda una PQRS nueva."""
    _validar(datos)
    pqrs = PQRS(**datos.model_dump(), radicado_por_id=radicado_por_id)
    db.add(pqrs)
    db.commit()
    db.refresh(pqrs)
    return pqrs
