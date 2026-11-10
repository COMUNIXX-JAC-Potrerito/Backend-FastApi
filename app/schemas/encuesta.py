import json
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.schemas.comunes import Codigo, Correo, DesdeORM, Nombre, Telefono, TextoLargo, Titulo

TextoPregunta = Annotated[str, Field(max_length=500)]
Opcion = Annotated[str, Field(max_length=200)]


# ---------- Crear ----------
class PreguntaCreate(BaseModel):
    texto: TextoPregunta
    tipo: Codigo = "texto"  # texto | opciones
    opciones: Annotated[list[Opcion], Field(max_length=50)] | None = None


class EncuestaCreate(BaseModel):
    titulo: Titulo
    descripcion: TextoLargo | None = None
    tipo: Codigo = "encuesta"  # encuesta | censo
    preguntas: Annotated[list[PreguntaCreate], Field(max_length=100)]


class PublicarEncuesta(BaseModel):
    publicada: bool


# ---------- Leer ----------
class PreguntaResponse(DesdeORM):
    id: int
    texto: str
    tipo: str
    opciones: list[str] | None = None
    orden: int

    @field_validator("opciones", mode="before")
    @classmethod
    def _opciones_desde_json(cls, valor):
        """En la base las opciones se guardan como texto JSON."""
        if valor is None or isinstance(valor, list):
            return valor
        try:
            lista = json.loads(valor)
        except TypeError, ValueError:
            return None
        return lista if isinstance(lista, list) else None


class EncuestaResumen(DesdeORM):
    id: int
    titulo: str
    descripcion: str | None = None
    tipo: str
    publicada: bool
    created_at: datetime


class EncuestaDetalle(EncuestaResumen):
    preguntas: list[PreguntaResponse] = []


# ---------- Responder ----------
class RespuestaItemCreate(BaseModel):
    pregunta_id: int
    valor: Annotated[str, Field(max_length=2_000)] | None = None


class ResponderEncuesta(BaseModel):
    items: Annotated[list[RespuestaItemCreate], Field(max_length=200)]
    # Datos personales (si hay sesión se toman de la cuenta).
    nombre: Nombre | None = None
    email: Correo | None = None
    telefono: Telefono | None = None


# ---------- Resultados ----------
class ResultadoPregunta(BaseModel):
    pregunta_id: int
    texto: str
    tipo: str
    total: int
    conteo: dict[str, int] | None = None  # para "opciones"
    respuestas_texto: list[str] | None = None  # para "texto"


class EncuestaResultados(BaseModel):
    encuesta_id: int
    titulo: str
    total_respuestas: int
    preguntas: list[ResultadoPregunta]


class ParticipanteResponse(DesdeORM):
    """Una persona que respondió la encuesta."""

    id: int
    nombre: str | None = None
    email: str | None = None
    telefono: str | None = None
    usuario_id: int | None = None
    created_at: datetime
