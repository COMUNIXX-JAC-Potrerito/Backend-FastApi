from datetime import datetime

from pydantic import BaseModel

from app.schemas.comunes import Codigo, DesdeORM, TextoLargo, Titulo


class ComunicacionCreate(BaseModel):
    tipo: Codigo  # enviada | recibida
    entidad: Titulo
    asunto: Titulo
    descripcion: TextoLargo | None = None
    fecha: datetime | None = None


class ComunicacionResponse(DesdeORM):
    id: int
    tipo: str
    entidad: str
    asunto: str
    descripcion: str | None = None
    fecha: datetime
    registrado_por_id: int | None = None
    created_at: datetime
