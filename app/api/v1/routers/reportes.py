from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.services.auth.roles import ROLES_GESTION
from app.services.reportes.reportes import resumen

router = APIRouter()


@router.get("/reportes/resumen")
def reporte_resumen(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    return resumen(db)
