"""Administración de usuarios: roles y comisiones (solo superadministradores)."""

import logging

from sqlalchemy.orm import Session

from app.core.errores import DatosInvalidos, NoEncontrado
from app.models.user import User
from app.services.auth.roles import ROL_SUPERADMIN, es_dignatario, es_rol_valido
from app.services.pqrs.catalogos import es_comite_valido

logger = logging.getLogger(__name__)


def listar_usuarios(db: Session) -> list[User]:
    return db.query(User).order_by(User.full_name, User.id).all()


def _obtener(db: Session, user_id: int) -> User:
    usuario = db.get(User, user_id)
    if usuario is None:
        raise NoEncontrado("Usuario no encontrado")
    return usuario


def _es_ultimo_superadmin(db: Session, usuario: User) -> bool:
    if usuario.role != ROL_SUPERADMIN:
        return False
    return db.query(User).filter(User.role == ROL_SUPERADMIN).count() <= 1


def cambiar_rol(db: Session, user_id: int, nuevo_rol: str, realizado_por_id: int) -> User:
    """Cambia el rol. Quien deja de ser dignatario pierde también su comisión."""
    if not es_rol_valido(nuevo_rol):
        raise DatosInvalidos("El rol indicado no es válido")
    usuario = _obtener(db, user_id)
    if nuevo_rol != ROL_SUPERADMIN and _es_ultimo_superadmin(db, usuario):
        raise DatosInvalidos("No se puede quitar el rol al único superadministrador")

    rol_anterior = usuario.role
    usuario.role = nuevo_rol
    if not es_dignatario(nuevo_rol):
        usuario.comite = None
    db.commit()
    db.refresh(usuario)
    logger.info(
        "Rol cambiado: usuario=%s %s -> %s (por usuario=%s)",
        user_id,
        rol_anterior,
        nuevo_rol,
        realizado_por_id,
    )
    return usuario


def cambiar_comite(db: Session, user_id: int, nuevo_comite: str, realizado_por_id: int) -> User:
    """Asigna o quita (cadena vacía) la comisión. Solo los dignatarios pueden tenerla."""
    comite = nuevo_comite.strip()
    if comite and not es_comite_valido(comite):
        raise DatosInvalidos("El comité/comisión indicado no es válido")
    usuario = _obtener(db, user_id)
    if comite and not es_dignatario(usuario.role):
        raise DatosInvalidos("Solo un dignatario (admin/superadmin) puede tener comisión")

    usuario.comite = comite or None
    db.commit()
    db.refresh(usuario)
    logger.info(
        "Comisión cambiada: usuario=%s -> %r (por usuario=%s)", user_id, usuario.comite, realizado_por_id
    )
    return usuario
