"""Tipos y bloques reutilizables de los esquemas de entrada/salida."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.core.config import settings

# Límites de longitud: evitan que una petición llene la base de datos.
Nombre = Annotated[str, Field(max_length=120)]
Correo = Annotated[str, Field(max_length=254)]
Telefono = Annotated[str, Field(max_length=30)]
Codigo = Annotated[str, Field(max_length=50)]  # tipos, estados, roles, categorías
Titulo = Annotated[str, Field(max_length=200)]
TextoLargo = Annotated[str, Field(max_length=5_000)]
TextoExtenso = Annotated[str, Field(max_length=20_000)]
# Texto obligatorio: se recortan espacios y no puede quedar vacío.
TextoRequerido = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5_000)]

_PREFIJO_CLOUDINARY = "https://res.cloudinary.com/"


def prefijo_adjuntos_permitido() -> str:
    """Solo se aceptan adjuntos alojados en la nube de Cloudinary del proyecto."""
    nube = settings.cloudinary_cloud_name
    return f"{_PREFIJO_CLOUDINARY}{nube}/" if nube else _PREFIJO_CLOUDINARY


class AdjuntoEntrada(BaseModel):
    """Adjunto opcional, subido antes con POST /api/uploads."""

    adjunto_url: str | None = Field(default=None, max_length=500)
    adjunto_tipo: str | None = Field(default=None, max_length=20)
    adjunto_nombre: str | None = Field(default=None, max_length=255)

    @field_validator("adjunto_url")
    @classmethod
    def _validar_url(cls, valor: str | None) -> str | None:
        if valor is None or not valor.strip():
            return None
        valor = valor.strip()
        if not valor.startswith(prefijo_adjuntos_permitido()):
            raise ValueError("el adjunto debe subirse primero con /api/uploads")
        return valor


class AdjuntoSalida(BaseModel):
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None


class DesdeORM(BaseModel):
    """Base de las respuestas que se construyen desde modelos SQLAlchemy."""

    model_config = ConfigDict(from_attributes=True)
