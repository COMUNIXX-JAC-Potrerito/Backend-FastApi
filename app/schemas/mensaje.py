from datetime import datetime

from pydantic import BaseModel

from app.schemas.comunes import AdjuntoEntrada, AdjuntoSalida, DesdeORM, TextoLargo, Titulo


class MensajeCreate(AdjuntoEntrada):
    destinatario_id: int
    # En el chat no hay "asunto"; se deja un valor por defecto.
    asunto: Titulo = "Chat"
    # Puede ir vacío si el mensaje es solo un adjunto (foto, audio...).
    contenido: TextoLargo = ""


class EditarMensaje(BaseModel):
    contenido: TextoLargo


class FijarMensaje(BaseModel):
    fijado: bool


class MensajeResponse(AdjuntoSalida, DesdeORM):
    id: int
    remitente_id: int
    destinatario_id: int
    asunto: str
    contenido: str
    leido: bool
    fijado: bool = False
    editado: bool = False
    created_at: datetime
