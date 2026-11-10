from pydantic import BaseModel

from app.schemas.comunes import TextoExtenso, TituloUnaLinea


class EnvioCreate(BaseModel):
    asunto: TituloUnaLinea
    contenido: TextoExtenso


class EnvioResultado(BaseModel):
    envio_id: int
    destinatarios: int
    modo: str  # simulado | real | parcial | error
