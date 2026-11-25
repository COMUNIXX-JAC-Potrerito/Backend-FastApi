"""Avisos de plazo legal de las PQRS: por vencer y vencidas.

Un bucle interno (cada hora) revisa las PQRS no finalizadas y avisa a la comisión
responsable. Es confiable porque UptimeRobot mantiene la instancia despierta. Se
marca cada PQRS para no repetir el aviso.
"""

import asyncio
import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.tiempo import ahora_utc
from app.db.session import SessionLocal
from app.models.pqrs import PQRS
from app.models.user import User
from app.services.auth.roles import ROL_SUPERADMIN
from app.services.envios.correo import enviar_correos
from app.services.notificaciones.plantillas import render_base
from app.services.notificaciones.pqrs import correos_del_comite
from app.services.pqrs.catalogos import ESTADO_FINALIZADA
from app.services.pqrs.plazos import fecha_limite, sumar_dias_habiles

logger = logging.getLogger(__name__)

DIAS_PREVIO = 5  # avisar cuando falten 5 días hábiles o menos
INTERVALO_SEGUNDOS = 3600  # revisión cada hora


def pqrs_por_avisar(db: Session, ahora) -> tuple[list[PQRS], list[PQRS]]:
    """PQRS que necesitan aviso: (por vencer, vencidas). Excluye finalizadas,
    Sugerencias y las que ya tienen su aviso enviado."""
    umbral_previo = sumar_dias_habiles(ahora, DIAS_PREVIO)
    previas, vencidas = [], []
    for pqrs in db.query(PQRS).filter(PQRS.estado != ESTADO_FINALIZADA).all():
        limite = fecha_limite(pqrs)
        if limite is None:
            continue
        if ahora >= limite:
            if not pqrs.aviso_vencido_enviado:
                vencidas.append(pqrs)
        elif limite <= umbral_previo and not pqrs.aviso_previo_enviado:
            previas.append(pqrs)
    return previas, vencidas


def _destinatarios(db: Session, pqrs: PQRS) -> list[str]:
    """La comisión responsable; si no tiene o no hay correos, los superadmins."""
    if pqrs.comite:
        correos = correos_del_comite(db, pqrs.comite)
        if correos:
            return correos
    filas = (
        db.query(User.email)
        .filter(User.role == ROL_SUPERADMIN, User.email.isnot(None), User.is_active.isnot(False))
        .all()
    )
    return [email for (email,) in filas]


def _cuerpo(pqrs: PQRS, vencida: bool) -> tuple[str, str]:
    limite = fecha_limite(pqrs)
    fecha_txt = limite.strftime("%d/%m/%Y") if limite else ""
    if vencida:
        titulo = "Una PQRS venció su plazo de respuesta"
        linea = f"El plazo legal de respuesta venció el {fecha_txt}. Atiéndela cuanto antes."
        asunto = f"Plazo VENCIDO · PQRS {pqrs.codigo_seguimiento}"
    else:
        titulo = "Una PQRS está por vencer su plazo"
        linea = f"El plazo legal de respuesta vence el {fecha_txt}."
        asunto = f"Plazo por vencer · PQRS {pqrs.codigo_seguimiento}"
    html = render_base(
        titulo,
        [linea, f"Tipo: {pqrs.tipo}", f"Asunto: {pqrs.asunto}", f"Código: {pqrs.codigo_seguimiento}"],
        cta_texto="Ir al panel",
        cta_url=settings.frontend_url,
    )
    return asunto, html


def revisar_plazos(db: Session) -> None:
    """Envía los avisos pendientes de plazo y marca cada PQRS para no repetir."""
    ahora = ahora_utc()
    previas, vencidas = pqrs_por_avisar(db, ahora)
    for pqrs in previas:
        _enviar(db, pqrs, vencida=False)
        pqrs.aviso_previo_enviado = True
    for pqrs in vencidas:
        _enviar(db, pqrs, vencida=True)
        pqrs.aviso_vencido_enviado = True
    if previas or vencidas:
        db.commit()


def _enviar(db: Session, pqrs: PQRS, vencida: bool) -> None:
    correos = _destinatarios(db, pqrs)
    if not correos:
        return
    asunto, html = _cuerpo(pqrs, vencida)
    estado = "venció" if vencida else "está por vencer"
    texto = f"La PQRS {pqrs.codigo_seguimiento} ({pqrs.tipo}) {estado} su plazo legal. Atiéndela en el panel."
    enviar_correos(correos, asunto, texto, html)


def _ciclo() -> None:
    with SessionLocal() as db:
        revisar_plazos(db)


async def iniciar_scheduler_plazos() -> None:
    """Revisa los plazos cada hora, sin bloquear el bucle de eventos."""
    while True:
        await asyncio.sleep(INTERVALO_SEGUNDOS)
        try:
            await asyncio.to_thread(_ciclo)
        except Exception:
            logger.exception("Error en el chequeo de plazos de PQRS")
