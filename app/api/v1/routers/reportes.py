from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.services.auth.roles import ROLES_GESTION
from app.services.reportes.reportes import carga_por_comite, resumen

router = APIRouter()


@router.get("/reportes/resumen")
def reporte_resumen(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    """Devuelve el resumen con los conteos del sistema (usuarios, PQRS, publicaciones, etc.)."""
    return resumen(db)


@router.get("/reportes/carga-comites")
def reporte_carga_comites(
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    """Trabajo pendiente de cada comité (para ver el flujo y la carga)."""
    return carga_por_comite(db)
