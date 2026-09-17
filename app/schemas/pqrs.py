from datetime import datetime

from pydantic import BaseModel


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
    created_at: datetime
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


class PQRSSeguimiento(BaseModel):
    # Respuesta pública: solo el avance, nunca la identidad de quien radicó
    codigo_seguimiento: str
    tipo: str
    asunto: str
    estado: str
    comite: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    # El radicador puede ver su propio adjunto al hacer seguimiento
    adjunto_url: str | None = None
    adjunto_tipo: str | None = None
    adjunto_nombre: str | None = None

    class Config:
        from_attributes = True
