from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    remitente_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destinatario_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asunto = Column(String, nullable=False)
    contenido = Column(String, nullable=False)
    leido = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Adjunto opcional (multimedia/archivo) subido a Cloudinary.
    adjunto_url = Column(String, nullable=True)
    adjunto_tipo = Column(String, nullable=True)   # image | video | raw
    adjunto_nombre = Column(String, nullable=True)
