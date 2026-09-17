from datetime import datetime

from pydantic import BaseModel


class MensajeCreate(BaseModel):
    destinatario_id: int
    asunto: str
    contenido: str


class MensajeResponse(BaseModel):
    id: int
    remitente_id: int
    destinatario_id: int
    asunto: str
    contenido: str
    leido: bool
    created_at: datetime

    class Config:
        from_attributes = True
