from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import requiere_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.envio import EnvioCreate, EnvioResultado
from app.services.auth.roles import ROLES_GESTION
from app.services.envios.gestion import enviar_masivo

router = APIRouter()


@router.post("/envios-masivos", response_model=EnvioResultado, status_code=status.HTTP_201_CREATED)
def enviar(
    data: EnvioCreate,
    db: Session = Depends(get_db),
    usuario: User = Depends(requiere_roles(*ROLES_GESTION)),
):
    # Envía a todos los usuarios registrados. Si no hay SMTP configurado,
    # queda en modo "simulado" (registra el envío sin mandar correos reales).
    return enviar_masivo(db, data.asunto, data.contenido, usuario.id)
