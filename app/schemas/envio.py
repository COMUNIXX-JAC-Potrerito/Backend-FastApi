from pydantic import BaseModel

from app.schemas.comunes import TextoExtenso, Titulo


class EnvioCreate(BaseModel):
    asunto: Titulo
    contenido: TextoExtenso


class EnvioResultado(BaseModel):
    envio_id: int
    destinatarios: int
    modo: str  # simulado | real | parcial | error
