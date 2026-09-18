from datetime import datetime

from pydantic import BaseModel


class MensajeCreate(BaseModel):
    destinatario_id: int
    # En el chat tipo WhatsApp no hay "asunto"; se deja un valor por defecto.
    asunto: str = "Chat"
    # El contenido puede ir vacío si el mensaje es solo un adjunto (foto, audio...).
    contenido: str = ""
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None


class EditarMensaje(BaseModel):
    contenido: str


class FijarMensaje(BaseModel):
    fijado: bool


class MensajeResponse(BaseModel):
    id: int
    remitente_id: int
    destinatario_id: int
    asunto: str
    contenido: str
    leido: bool
    fijado: bool = False
    editado: bool = False
    created_at: datetime
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None

    class Config:
        from_attributes = True
