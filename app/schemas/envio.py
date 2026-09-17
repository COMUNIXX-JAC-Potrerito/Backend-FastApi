from pydantic import BaseModel


class EnvioCreate(BaseModel):
    asunto: str
    contenido: str


class EnvioResultado(BaseModel):
    envio_id: int
    destinatarios: int
    modo: str  # simulado, real, error
