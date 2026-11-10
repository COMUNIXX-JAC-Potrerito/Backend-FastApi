from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.core.tiempo import ahora_utc
from app.db.session import Base
from app.models.mixins import AdjuntoMixin


class Mensaje(AdjuntoMixin, Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    remitente_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destinatario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asunto = Column(String, nullable=False)
    contenido = Column(String, nullable=False)
    leido = Column(Boolean, default=False)
    fijado = Column(Boolean, default=False)
    editado = Column(Boolean, default=False)
    created_at = Column(DateTime, default=ahora_utc)
