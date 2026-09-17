from datetime import datetime

from pydantic import BaseModel


class PublicacionCreate(BaseModel):
    categoria: str
    titulo: str
    contenido: str
    fecha_evento: datetime | None = None
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None


class PublicacionResponse(BaseModel):
    id: int
    categoria: str
    titulo: str
    contenido: str
    fecha_evento: datetime | None = None
    publicado_por_id: int | None = None
    created_at: datetime
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None

    class Config:
        from_attributes = True
