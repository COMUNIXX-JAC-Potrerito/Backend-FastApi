from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.core.tiempo import ahora_utc
from app.db.session import Base


class Encuesta(Base):
    __tablename__ = "encuestas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    tipo = Column(String, nullable=False, default="encuesta")  # encuesta | censo
    publicada = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=ahora_utc)

    preguntas = relationship("Pregunta", order_by="Pregunta.orden", cascade="all, delete-orphan")


class Pregunta(Base):
    __tablename__ = "preguntas"

    id = Column(Integer, primary_key=True, index=True)
    encuesta_id = Column(Integer, ForeignKey("encuestas.id"), nullable=False)
    texto = Column(String, nullable=False)
    tipo = Column(String, nullable=False, default="texto")  # texto | opciones
    opciones = Column(String, nullable=True)  # lista JSON, solo para tipo "opciones"
    orden = Column(Integer, default=0)


class RespuestaEncuesta(Base):
    __tablename__ = "respuestas_encuesta"
    # Una cuenta responde cada encuesta una sola vez, aunque lleguen dos envíos a la
    # vez. Las respuestas sin cuenta (usuario_id NULL) no chocan: NULL no se repite.
    __table_args__ = (
        Index("uq_respuestas_encuesta_encuesta_usuario", "encuesta_id", "usuario_id", unique=True),
    )

    id = Column(Integer, primary_key=True, index=True)
    encuesta_id = Column(Integer, ForeignKey("encuestas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Datos de quien responde (identifican la participación).
    nombre = Column(String, nullable=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    created_at = Column(DateTime, default=ahora_utc)


class RespuestaItem(Base):
    __tablename__ = "respuesta_items"

    id = Column(Integer, primary_key=True, index=True)
    respuesta_id = Column(Integer, ForeignKey("respuestas_encuesta.id"), nullable=False)
    pregunta_id = Column(Integer, ForeignKey("preguntas.id"), nullable=False)
    valor = Column(String, nullable=True)
