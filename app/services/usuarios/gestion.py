from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth.roles import ROLES_GESTION, es_rol_valido
from app.services.pqrs.catalogos import es_comite_valido


def cambiar_rol(db: Session, user_id: int, nuevo_rol: str):
    if not es_rol_valido(nuevo_rol):
        raise ValueError("El rol indicado no es válido")

    usuario = db.query(User).filter(User.id == user_id).first()
    if usuario is None:
        return None

    usuario.role = nuevo_rol
    db.commit()
    db.refresh(usuario)
    return usuario


def cambiar_comite(db: Session, user_id: int, nuevo_comite: str):
    # Cadena vacía = quitar la comisión.
    comite = nuevo_comite.strip()
    if comite and not es_comite_valido(comite):
        raise ValueError("El comité/comisión indicado no es válido")

    usuario = db.query(User).filter(User.id == user_id).first()
    if usuario is None:
        return None

    # Solo los dignatarios (admin/superadmin) pueden pertenecer a una comisión.
    if comite and usuario.role not in ROLES_GESTION:
        raise ValueError("Solo un dignatario (admin/superadmin) puede tener comisión")

    usuario.comite = comite or None
    db.commit()
    db.refresh(usuario)
    return usuario
