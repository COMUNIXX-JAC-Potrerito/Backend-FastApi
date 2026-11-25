"""Recuperación de contraseña: solicitud (envía enlace) y restablecimiento."""

import hashlib
import secrets
from datetime import timedelta

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errores import DatosInvalidos
from app.core.tiempo import ahora_utc
from app.models.recuperacion import PasswordResetToken
from app.models.user import User
from app.services.auth.gestion import buscar_por_email
from app.services.auth.seguridad import hash_password
from app.services.auth.validaciones import is_password_strong
from app.services.envios.correo import enviar_correos
from app.services.notificaciones.plantillas import render_base

VIGENCIA = timedelta(hours=1)
_MENSAJE_INVALIDO = "El enlace de recuperación no es válido o ya venció"


def hash_token(token: str) -> str:
    """Hash del token para guardar en la base (nunca el token en claro)."""
    return hashlib.sha256(token.encode()).hexdigest()


def solicitar_recuperacion(db: Session, email: str, background_tasks: BackgroundTasks) -> None:
    """Crea un token y agenda el correo con el enlace. Silencioso si el correo
    no existe o la cuenta está inactiva (para no revelar qué correos hay)."""
    usuario = buscar_por_email(db, email)
    if usuario is None or not usuario.esta_activo:
        return

    token = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=usuario.id,
            token_hash=hash_token(token),
            expires_at=ahora_utc() + VIGENCIA,
        )
    )
    db.commit()

    enlace = f"{settings.frontend_url}/restablecer?token={token}"
    html = render_base(
        "Restablece tu contraseña",
        [
            "Recibimos una solicitud para restablecer tu contraseña en COMUNIX.",
            "Haz clic en el botón para crear una nueva. El enlace vence en 1 hora.",
            "Si no fuiste tú, ignora este correo: tu contraseña no cambiará.",
        ],
        cta_texto="Restablecer contraseña",
        cta_url=enlace,
    )
    texto = f"Restablece tu contraseña en COMUNIX: {enlace} (el enlace vence en 1 hora)."
    background_tasks.add_task(
        enviar_correos, [usuario.email], "Restablece tu contraseña · COMUNIX", texto, html
    )


def restablecer_password(db: Session, token: str, password: str) -> None:
    """Valida el token (existe, no usado, no vencido) y cambia la contraseña."""
    registro = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == hash_token(token))
        .first()
    )
    if registro is None or registro.used_at is not None or registro.expires_at < ahora_utc():
        raise DatosInvalidos(_MENSAJE_INVALIDO)
    if not is_password_strong(password):
        raise DatosInvalidos("La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número")
    usuario = db.get(User, registro.user_id)
    if usuario is None:
        raise DatosInvalidos(_MENSAJE_INVALIDO)
    usuario.hashed_password = hash_password(password)
    registro.used_at = ahora_utc()
    db.commit()
