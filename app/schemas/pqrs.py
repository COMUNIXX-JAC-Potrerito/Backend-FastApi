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

    class Config:
        from_attributes = True
