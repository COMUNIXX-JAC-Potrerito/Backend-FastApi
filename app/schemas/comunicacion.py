from datetime import datetime

from pydantic import BaseModel


class ComunicacionCreate(BaseModel):
    tipo: str  # enviada, recibida
    entidad: str
    asunto: str
    descripcion: str | None = None
    fecha: datetime | None = None


class ComunicacionResponse(BaseModel):
    id: int
    tipo: str
    entidad: str
    asunto: str
    descripcion: str | None = None
    fecha: datetime
    registrado_por_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True
