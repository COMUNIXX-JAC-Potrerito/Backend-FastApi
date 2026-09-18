from datetime import datetime

from pydantic import BaseModel


# ---------- Crear ----------
class PreguntaCreate(BaseModel):
    texto: str
    tipo: str = "texto"  # texto | opciones
    opciones: list[str] | None = None


class EncuestaCreate(BaseModel):
    titulo: str
    descripcion: str | None = None
    tipo: str = "encuesta"  # encuesta | censo
    preguntas: list[PreguntaCreate]


class PublicarEncuesta(BaseModel):
    publicada: bool


# ---------- Leer ----------
class PreguntaResponse(BaseModel):
    id: int
    texto: str
    tipo: str
    opciones: list[str] | None = None
    orden: int


class EncuestaResumen(BaseModel):
    id: int
    titulo: str
    descripcion: str | None = None
    tipo: str
    publicada: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EncuestaDetalle(EncuestaResumen):
    preguntas: list[PreguntaResponse] = []


# ---------- Responder ----------
class RespuestaItemCreate(BaseModel):
    pregunta_id: int
    valor: str | None = None


class ResponderEncuesta(BaseModel):
    items: list[RespuestaItemCreate]


# ---------- Resultados ----------
class ResultadoPregunta(BaseModel):
    pregunta_id: int
    texto: str
    tipo: str
    total: int
    conteo: dict[str, int] | None = None       # para "opciones"
    respuestas_texto: list[str] | None = None  # para "texto"


class EncuestaResultados(BaseModel):
    encuesta_id: int
    titulo: str
    total_respuestas: int
    preguntas: list[ResultadoPregunta]
