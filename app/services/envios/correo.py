"""Envío de correos por SMTP."""

import logging
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

TIEMPO_ESPERA_SEGUNDOS = 30


@dataclass(frozen=True)
class ResultadoEnvio:
    enviados: int
    fallidos: int
    modo: str  # simulado | real | parcial | error


def _modo(enviados: int, fallidos: int) -> str:
    if fallidos == 0:
        return "real"
    return "parcial" if enviados else "error"


def enviar_correos(destinatarios: list[str], asunto: str, contenido: str) -> ResultadoEnvio:
    """Envía un correo a cada destinatario.

    Sin SMTP configurado funciona en modo "simulado" (no envía nada). La conexión
    exige TLS con certificado verificado para no exponer la contraseña SMTP.
    """
    if not settings.smtp_host or not settings.smtp_user:
        return ResultadoEnvio(enviados=0, fallidos=0, modo="simulado")

    remitente = settings.smtp_from or settings.smtp_user
    enviados = fallidos = 0
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=TIEMPO_ESPERA_SEGUNDOS) as servidor:
            servidor.starttls(context=ssl.create_default_context())
            servidor.login(settings.smtp_user, settings.smtp_password or "")
            for correo in destinatarios:
                mensaje = EmailMessage()
                mensaje["Subject"] = asunto
                mensaje["From"] = remitente
                mensaje["To"] = correo
                mensaje.set_content(contenido)
                try:
                    servidor.send_message(mensaje)
                    enviados += 1
                except smtplib.SMTPException:
                    fallidos += 1
                    logger.warning("No se pudo enviar el correo a un destinatario", exc_info=True)
    except OSError, smtplib.SMTPException, ValueError:
        logger.exception("Fallo de conexión SMTP durante el envío masivo")
        return ResultadoEnvio(enviados=enviados, fallidos=len(destinatarios) - enviados, modo="error")

    return ResultadoEnvio(enviados=enviados, fallidos=fallidos, modo=_modo(enviados, fallidos))
