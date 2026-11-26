from typing import Literal

from pydantic import BaseModel

from app.schemas.comunes import TextoExtenso, TituloUnaLinea

# Público dirigido del comunicado: todos los usuarios (sin entidades externas) o
# solo los miembros de la JAC (dignatarios).
Publico = Literal["todos", "jac"]


class EnvioCreate(BaseModel):
    asunto: TituloUnaLinea
    contenido: TextoExtenso
    publico: Publico = "todos"
    guardar_en_bitacora: bool = False


class EnvioResultado(BaseModel):
    envio_id: int
    destinatarios: int
    modo: str  # simulado | real | parcial | error
    guardado_en_bitacora: bool = False
