"""Avisos por correo a la comunidad: nueva encuesta o publicación.

Como en los avisos de PQRS, el router arma el envío con la sesión de la petición
y deja solo el envío SMTP a BackgroundTasks.
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.encuesta import Encuesta
from app.models.publicacion import Publicacion
from app.models.user import User
from app.services.notificaciones.plantillas import render_base

Envio = tuple[list[str], str, str, str]  # (destinatarios, asunto, texto, html)


def correos_activos(db: Session) -> list[str]:
    """Correos de todos los usuarios activos (la comunidad registrada)."""
    filas = (
        db.query(User.email)
        .filter(User.email.isnot(None), User.is_active.isnot(False))
        .all()
    )
    return [email for (email,) in filas]


def cuerpo_encuesta(encuesta: Encuesta) -> tuple[str, str]:
    tipo = "censo" if encuesta.tipo == "censo" else "encuesta"
    asunto = f"Nueva {tipo} de la JAC · {encuesta.titulo}"
    html = render_base(
        f"Nueva {tipo}: {encuesta.titulo}",
        ["La Junta de Acción Comunal publicó una nueva consulta para la comunidad.",
         "Tu opinión cuenta: participa desde COMUNIX."],
        cta_texto="Participar",
        cta_url=f"{settings.frontend_url}/encuestas",
    )
    return asunto, html


def cuerpo_publicacion(publicacion: Publicacion) -> tuple[str, str]:
    asunto = f"Nueva publicación de la JAC · {publicacion.titulo}"
    html = render_base(
        f"Nueva publicación: {publicacion.titulo}",
        ["La Junta de Acción Comunal publicó algo nuevo en la cartelera comunitaria."],
        cta_texto="Ver publicación",
        cta_url=f"{settings.frontend_url}/publicaciones",
    )
    return asunto, html


def preparar_nueva_encuesta(db: Session, encuesta_id: int) -> Envio | None:
    encuesta = db.get(Encuesta, encuesta_id)
    if encuesta is None:
        return None
    correos = correos_activos(db)
    if not correos:
        return None
    asunto, html = cuerpo_encuesta(encuesta)
    texto = f"Nueva consulta de la JAC: {encuesta.titulo}. Participa en {settings.frontend_url}/encuestas"
    return correos, asunto, texto, html


def preparar_nueva_publicacion(db: Session, publicacion_id: int) -> Envio | None:
    publicacion = db.get(Publicacion, publicacion_id)
    if publicacion is None:
        return None
    correos = correos_activos(db)
    if not correos:
        return None
    asunto, html = cuerpo_publicacion(publicacion)
    texto = f"Nueva publicación de la JAC: {publicacion.titulo}. Léela en {settings.frontend_url}/publicaciones"
    return correos, asunto, texto, html
