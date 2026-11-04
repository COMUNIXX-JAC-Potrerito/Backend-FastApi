from datetime import datetime

from pydantic import BaseModel


class RespuestaResponse(BaseModel):
    # Una respuesta de la JAC dentro del hilo de una PQRS
    id: int
    texto: str
    autor_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class PQRSResponse(BaseModel):
    id: int
    codigo_seguimiento: str
    tipo: str
    asunto: str
    descripcion: str
    estado: str
    es_anonima: bool
    comite: str | None = None
    # Datos de identidad: llegan en None cuando la PQRS es anónima
    radicado_por_id: int | None = None
    nombre_contacto: str | None = None
    email_contacto: str | None = None
    telefono_contacto: str | None = None
    created_at: datetime  # fecha y hora de radicación
    updated_at: datetime | None = None  # fecha y hora de la última actualización
    respuesta: str | None = None  # legado (respuesta única); usar "respuestas"
    respuesta_fecha: datetime | None = None
    respuestas: list[RespuestaResponse] = []  # hilo de respuestas de la JAC
    # Adjunto opcional (multimedia/archivo)
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None

    class Config:
        from_attributes = True


class PQRSCreate(BaseModel):
    tipo: str
    asunto: str
    descripcion: str
    es_anonima: bool = False
    # Datos de contacto para no registrados o para poder notificar
    nombre_contacto: str | None = None
    email_contacto: str | None = None
    telefono_contacto: str | None = None
    # Adjunto opcional (multimedia/archivo) subido antes vía /api/uploads
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None


class AsignarComite(BaseModel):
    comite: str


class CambiarEstado(BaseModel):
    estado: str


class ResponderPQRS(BaseModel):
    respuesta: str


class PQRSSeguimiento(BaseModel):
    # Respuesta pública: solo el avance, nunca la identidad de quien radicó
    codigo_seguimiento: str
    tipo: str
    asunto: str
    estado: str
    comite: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    respuesta: str | None = None  # legado; usar "respuestas"
    respuestas: list[RespuestaResponse] = []  # hilo de respuestas de la JAC, visible al ciudadano
    # El radicador puede ver su propio adjunto al hacer seguimiento
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None

    class Config:
        from_attributes = True
