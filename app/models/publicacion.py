from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class Publicacion(Base):
    __tablename__ = "publicaciones"

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, nullable=False)  # decision, actividad, contenido
    titulo = Column(String, nullable=False)
    contenido = Column(String, nullable=False)
    fecha_evento = Column(DateTime, nullable=True)  # solo para actividades
    publicado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Adjunto opcional (imagen/video/documento) subido a Cloudinary.
    adjunto_url = Column(String, nullable=True)
    adjunto_tipo = Column(String, nullable=True)   # image | video | raw
    adjunto_nombre = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
