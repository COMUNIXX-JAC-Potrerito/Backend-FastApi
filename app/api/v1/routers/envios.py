"""Envío masivo de comunicados por correo (solo dignatarios)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import solo_dignatarios
from app.db.session import get_db
from app.models.user import User
from app.schemas.envio import EnvioCreate, EnvioResultado
from app.services.envios.gestion import enviar_masivo

router = APIRouter(tags=["envios"])


@router.post("/envios-masivos", response_model=EnvioResultado, status_code=status.HTTP_201_CREATED)
def enviar(data: EnvioCreate, db: Session = Depends(get_db), usuario: User = Depends(solo_dignatarios)):
    """Envía el comunicado a todos los usuarios activos.

    Sin SMTP configurado queda en modo "simulado" (registra el envío sin mandar correos).
    """
    return enviar_masivo(db, data, usuario.id)
