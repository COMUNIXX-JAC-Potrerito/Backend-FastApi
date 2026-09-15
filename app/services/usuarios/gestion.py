from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth.roles import es_rol_valido


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
