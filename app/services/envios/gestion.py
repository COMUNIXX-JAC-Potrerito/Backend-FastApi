"""Envío masivo de comunicados por correo a los usuarios registrados."""

import logging

from sqlalchemy.orm import Session

from app.models.envio_masivo import EnvioMasivo
from app.models.user import User
from app.schemas.envio import EnvioCreate
from app.services.envios.correo import enviar_correos

logger = logging.getLogger(__name__)


def _correos_activos(db: Session) -> list[str]:
    usuarios = db.query(User.email).filter(User.email.isnot(None), User.is_active.isnot(False)).all()
    return [email for (email,) in usuarios]


def enviar_masivo(db: Session, datos: EnvioCreate, enviado_por_id: int) -> dict:
    """Envía el comunicado a todos los usuarios activos y guarda el registro."""
    correos = _correos_activos(db)
    resultado = enviar_correos(correos, datos.asunto, datos.contenido)

    envio = EnvioMasivo(
        asunto=datos.asunto,
        contenido=datos.contenido,
        destinatarios=len(correos),
        modo=resultado.modo,
        enviado_por_id=enviado_por_id,
    )
    db.add(envio)
    db.commit()
    db.refresh(envio)
    logger.info(
        "Envío masivo %s: modo=%s enviados=%s fallidos=%s (por usuario=%s)",
        envio.id,
        resultado.modo,
        resultado.enviados,
        resultado.fallidos,
        enviado_por_id,
    )
    return {"envio_id": envio.id, "destinatarios": len(correos), "modo": resultado.modo}
