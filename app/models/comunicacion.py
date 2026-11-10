from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.tiempo import ahora_utc
from app.db.session import Base


class Comunicacion(Base):
    __tablename__ = "comunicaciones"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # enviada | recibida
    entidad = Column(String, nullable=False)  # entidad externa
    asunto = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    fecha = Column(DateTime, default=ahora_utc)
    registrado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=ahora_utc)
