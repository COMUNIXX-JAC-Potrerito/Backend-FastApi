from sqlalchemy.orm import Session

from app.models.envio_masivo import EnvioMasivo
from app.models.user import User
from app.services.envios.correo import enviar_correos


def enviar_masivo(db: Session, asunto: str, contenido: str, enviado_por_id: int | None):
    # Destinatarios = todos los usuarios registrados con correo
    correos = [u.email for u in db.query(User).filter(User.email.isnot(None)).all()]

    modo = enviar_correos(correos, asunto, contenido)

    envio = EnvioMasivo(
        asunto=asunto,
        contenido=contenido,
        destinatarios=len(correos),
        modo=modo,
        enviado_por_id=enviado_por_id,
    )
    db.add(envio)
    db.commit()
    db.refresh(envio)

    return {"envio_id": envio.id, "destinatarios": len(correos), "modo": modo}
