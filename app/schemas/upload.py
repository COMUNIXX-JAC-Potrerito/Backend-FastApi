from pydantic import BaseModel


class AdjuntoResponse(BaseModel):
    """Datos que devuelve POST /api/uploads tras subir un archivo."""

    url: str
    tipo: str   # 'image' | 'video' | 'raw'
    nombre: str
