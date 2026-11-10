from datetime import datetime

from app.schemas.comunes import AdjuntoEntrada, AdjuntoSalida, Codigo, DesdeORM, TextoExtenso, Titulo


class PublicacionCreate(AdjuntoEntrada):
    categoria: Codigo
    titulo: Titulo
    contenido: TextoExtenso
    fecha_evento: datetime | None = None


class PublicacionResponse(AdjuntoSalida, DesdeORM):
    id: int
    categoria: str
    titulo: str
    contenido: str
    fecha_evento: datetime | None = None
    publicado_por_id: int | None = None
    created_at: datetime
