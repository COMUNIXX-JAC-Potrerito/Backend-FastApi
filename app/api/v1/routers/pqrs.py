from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.pqrs import PQRSResponse
from app.services.pqrs.gestion import listar_entrantes

router = APIRouter()


@router.get("/pqrs/entrantes", response_model=list[PQRSResponse])
def pqrs_entrantes(db: Session = Depends(get_db)):
    return listar_entrantes(db)
