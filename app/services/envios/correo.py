import smtplib
from email.message import EmailMessage

from app.core.config import settings


def enviar_correos(destinatarios: list[str], asunto: str, contenido: str) -> str:
    """Envía el correo a la lista de destinatarios.
    Si no hay SMTP configurado, funciona en modo 'simulado' (no envía nada).
    Devuelve el modo: 'simulado', 'real' o 'error'.
    """
    if not settings.smtp_host or not settings.smtp_user:
        return "simulado"

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password or "")
            remitente = settings.smtp_from or settings.smtp_user
            for correo in destinatarios:
                mensaje = EmailMessage()
                mensaje["Subject"] = asunto
                mensaje["From"] = remitente
                mensaje["To"] = correo
                mensaje.set_content(contenido)
                server.send_message(mensaje)
        return "real"
    except Exception:
        return "error"
