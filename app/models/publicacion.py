from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.tiempo import ahora_utc
from app.db.session import Base
from app.models.mixins import AdjuntoMixin


class Publicacion(AdjuntoMixin, Base):
    __tablename__ = "publicaciones"

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, nullable=False)  # decision | actividad | contenido
    titulo = Column(String, nullable=False)
    contenido = Column(String, nullable=False)
    fecha_evento = Column(DateTime, nullable=True)  # solo para actividades
    publicado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=ahora_utc)
    updated_at = Column(DateTime, default=ahora_utc, onupdate=ahora_utc)
