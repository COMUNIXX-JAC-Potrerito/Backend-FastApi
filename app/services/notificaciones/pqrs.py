"""Avisos por correo de PQRS: asignación a la comisión y actualización al ciudadano.

El router arma el envío (consulta + contenido) con la sesión de la petición y
deja solo el envío SMTP a BackgroundTasks, para no bloquear la API y para que la
lógica sea probable con la base de pruebas.
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pqrs import PQRS
from app.models.user import User
from app.services.notificaciones.plantillas import render_base
from app.services.pqrs.catalogos import ESTADO_FINALIZADA

Envio = tuple[list[str], str, str, str]  # (destinatarios, asunto, texto, html)


def correos_del_comite(db: Session, comite: str) -> list[str]:
    """Correos de los dignatarios activos de una comisión."""
    filas = (
        db.query(User.email)
        .filter(
            User.comite == comite,
            User.email.isnot(None),
            User.is_active.isnot(False),
        )
        .all()
    )
    return [email for (email,) in filas]


def cuerpo_asignacion(pqrs: PQRS) -> tuple[str, str]:
    """Asunto y HTML del aviso a la comisión. No revela la identidad del ciudadano."""
    asunto = f"Nueva PQRS asignada a tu comisión · {pqrs.codigo_seguimiento}"
    html = render_base(
        "Se asignó una PQRS a tu comisión",
        [
            f"Tipo: {pqrs.tipo}",
            f"Asunto: {pqrs.asunto}",
            f"Código de seguimiento: {pqrs.codigo_seguimiento}",
            "Entra al panel de la JAC para gestionarla.",
        ],
        cta_texto="Ir al panel",
        cta_url=settings.frontend_url,
    )
    return asunto, html


def cuerpo_actualizacion(pqrs: PQRS, cambio: str) -> tuple[str, str]:
    """Asunto y HTML del aviso al ciudadano (cambio ∈ {"respuesta", "estado"})."""
    if cambio == "respuesta":
        titulo = "Tu PQRS tiene una nueva respuesta"
        linea = "La Junta de Acción Comunal respondió tu solicitud."
    elif pqrs.estado == ESTADO_FINALIZADA:
        titulo = "Tu PQRS fue finalizada"
        linea = "Tu solicitud fue marcada como finalizada."
    else:
        titulo = "El estado de tu PQRS cambió"
        linea = f"El nuevo estado de tu solicitud es: {pqrs.estado}."
    enlace = f"{settings.frontend_url}/consultar?codigo={pqrs.codigo_seguimiento}"
    asunto = f"Novedad en tu PQRS · {pqrs.codigo_seguimiento}"
    html = render_base(
        titulo,
        [linea, f"Código de seguimiento: {pqrs.codigo_seguimiento}"],
        cta_texto="Ver mi PQRS",
        cta_url=enlace,
    )
    return asunto, html


def preparar_asignacion(db: Session, pqrs_id: int) -> Envio | None:
    """Datos del correo a la comisión, o None si no hay a quién avisar."""
    pqrs = db.get(PQRS, pqrs_id)
    if pqrs is None or not pqrs.comite:
        return None
    correos = correos_del_comite(db, pqrs.comite)
    if not correos:
        return None
    asunto, html = cuerpo_asignacion(pqrs)
    texto = (
        f"Se asignó una PQRS a tu comisión. Tipo: {pqrs.tipo}. "
        f"Código: {pqrs.codigo_seguimiento}. Entra al panel de la JAC."
    )
    return correos, asunto, texto, html


def preparar_actualizacion_ciudadano(db: Session, pqrs_id: int, cambio: str) -> Envio | None:
    """Datos del correo al ciudadano (incluye anónimas), o None si no dio correo."""
    pqrs = db.get(PQRS, pqrs_id)
    if pqrs is None or not pqrs.email_contacto:
        return None
    asunto, html = cuerpo_actualizacion(pqrs, cambio)
    enlace = f"{settings.frontend_url}/consultar?codigo={pqrs.codigo_seguimiento}"
    texto = f"Novedad en tu PQRS {pqrs.codigo_seguimiento}. Consúltala en {enlace}"
    return [pqrs.email_contacto], asunto, texto, html
