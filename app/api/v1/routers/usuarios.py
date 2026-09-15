from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import CambiarRol, UserResponse
from app.services.auth.roles import ROL_SUPERADMIN
from app.services.usuarios.gestion import cambiar_rol

router = APIRouter()


# Solo un superadministrador puede cambiar el rol de un usuario.
@router.put("/usuarios/{user_id}/rol", response_model=UserResponse)
def actualizar_rol(
    user_id: int,
    data: CambiarRol,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(ROL_SUPERADMIN)),
):
    try:
        actualizado = cambiar_rol(db, user_id, data.rol)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    if actualizado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return actualizado
