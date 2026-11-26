"""Envío masivo de comunicados por correo a los usuarios registrados."""

import logging

from sqlalchemy.orm import Session

from app.models.comunicacion import Comunicacion
from app.models.envio_masivo import EnvioMasivo
from app.models.user import User
from app.schemas.envio import EnvioCreate
from app.services.auth.roles import ROL_ENTIDAD, ROLES_GESTION
from app.services.envios.correo import enviar_correos

logger = logging.getLogger(__name__)

# Etiqueta que queda en la bitácora (campo "entidad") según el público elegido.
_ETIQUETA_PUBLICO = {
    "todos": "Comunidad — todos los usuarios",
    "jac": "Miembros de la JAC",
}


def _correos(db: Session, publico: str) -> list[str]:
    """Correos de los destinatarios según el público: 'jac' = dignatarios;
    'todos' = cualquier rol activo con correo, salvo las cuentas de entidad."""
    consulta = db.query(User.email).filter(User.email.isnot(None), User.is_active.isnot(False))
    if publico == "jac":
        consulta = consulta.filter(User.role.in_(ROLES_GESTION))
    else:
        consulta = consulta.filter(User.role != ROL_ENTIDAD)
    return [email for (email,) in consulta.all()]


def enviar_masivo(db: Session, datos: EnvioCreate, enviado_por_id: int) -> dict:
    """Envía el comunicado al público elegido y guarda el registro. Si se pide,
    también deja constancia en la bitácora de comunicaciones."""
    correos = _correos(db, datos.publico)
    resultado = enviar_correos(correos, datos.asunto, datos.contenido)

    envio = EnvioMasivo(
        asunto=datos.asunto,
        contenido=datos.contenido,
        destinatarios=len(correos),
        modo=resultado.modo,
        enviado_por_id=enviado_por_id,
    )
    db.add(envio)
    if datos.guardar_en_bitacora:
        db.add(
            Comunicacion(
                tipo="enviada",
                entidad=_ETIQUETA_PUBLICO.get(datos.publico, datos.publico),
                asunto=datos.asunto,
                descripcion=datos.contenido,
                registrado_por_id=enviado_por_id,
            )
        )
    db.commit()
    db.refresh(envio)
    logger.info(
        "Envío masivo %s: modo=%s enviados=%s fallidos=%s publico=%s bitacora=%s (por usuario=%s)",
        envio.id,
        resultado.modo,
        resultado.enviados,
        resultado.fallidos,
        datos.publico,
        datos.guardar_en_bitacora,
        enviado_por_id,
    )
    return {
        "envio_id": envio.id,
        "destinatarios": len(correos),
        "modo": resultado.modo,
        "guardado_en_bitacora": datos.guardar_en_bitacora,
    }
