from datetime import datetime

from pydantic import BaseModel


class PublicacionCreate(BaseModel):
    categoria: str
    titulo: str
    contenido: str
    fecha_evento: datetime | None = None


class PublicacionResponse(BaseModel):
    id: int
    categoria: str
    titulo: str
    contenido: str
    fecha_evento: datetime | None = None
    publicado_por_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True
