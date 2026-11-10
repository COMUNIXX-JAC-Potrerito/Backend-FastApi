"""Indicadores del panel de información general (solo dignatarios)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import solo_dignatarios
from app.db.session import get_db
from app.services.reportes.reportes import carga_por_comite, resumen

router = APIRouter(tags=["reportes"], dependencies=[Depends(solo_dignatarios)])


@router.get("/reportes/resumen")
def reporte_resumen(db: Session = Depends(get_db)):
    """Conteos generales: usuarios, PQRS por estado, publicaciones, etc."""
    return resumen(db)


@router.get("/reportes/carga-comites")
def reporte_carga_comites(db: Session = Depends(get_db)):
    """Trabajo pendiente de cada comité."""
    return carga_por_comite(db)
