from datetime import datetime

from pydantic import BaseModel

from app.schemas.comunes import (
    AdjuntoEntrada,
    AdjuntoSalida,
    Codigo,
    Correo,
    DesdeORM,
    Nombre,
    Telefono,
    TextoLargo,
    TextoRequerido,
    Titulo,
)


class RespuestaResponse(DesdeORM):
    """Una respuesta de la JAC dentro del hilo de una PQRS."""

    id: int
    texto: str
    autor_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None


class PQRSResponse(AdjuntoSalida, DesdeORM):
    id: int
    codigo_seguimiento: str
    tipo: str
    asunto: str
    descripcion: str
    estado: str
    es_anonima: bool
    comite: str | None = None
    # Datos de identidad: llegan en None cuando la PQRS es anónima.
    radicado_por_id: int | None = None
    nombre_contacto: str | None = None
    email_contacto: str | None = None
    telefono_contacto: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    respuesta: str | None = None  # versión anterior (respuesta única); usar "respuestas"
    respuesta_fecha: datetime | None = None
    respuestas: list[RespuestaResponse] = []


class PQRSCreate(AdjuntoEntrada):
    tipo: Codigo
    asunto: Titulo
    descripcion: TextoLargo
    es_anonima: bool = False
    # Contacto: obligatorio si no es anónima (nombre + correo o teléfono).
    nombre_contacto: Nombre | None = None
    email_contacto: Correo | None = None
    telefono_contacto: Telefono | None = None


class AsignarComite(BaseModel):
    comite: Titulo


class CambiarEstado(BaseModel):
    estado: Codigo


class ResponderPQRS(BaseModel):
    respuesta: TextoRequerido


class PQRSSeguimiento(AdjuntoSalida, DesdeORM):
    """Consulta pública: solo el avance, nunca la identidad de quien radicó."""

    codigo_seguimiento: str
    tipo: str
    asunto: str
    estado: str
    comite: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    respuesta: str | None = None  # versión anterior; usar "respuestas"
    respuestas: list[RespuestaResponse] = []
