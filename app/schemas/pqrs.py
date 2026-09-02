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
