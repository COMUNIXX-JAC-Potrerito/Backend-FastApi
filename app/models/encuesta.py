from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class Encuesta(Base):
    __tablename__ = "encuestas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    tipo = Column(String, nullable=False, default="encuesta")  # encuesta | censo
    publicada = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Pregunta(Base):
    __tablename__ = "preguntas"

    id = Column(Integer, primary_key=True, index=True)
    encuesta_id = Column(Integer, ForeignKey("encuestas.id"), nullable=False)
    texto = Column(String, nullable=False)
    tipo = Column(String, nullable=False, default="texto")  # texto | opciones
    # Para tipo "opciones": lista de opciones guardada como JSON (texto).
    opciones = Column(String, nullable=True)
    orden = Column(Integer, default=0)


class RespuestaEncuesta(Base):
    __tablename__ = "respuestas_encuesta"

    id = Column(Integer, primary_key=True, index=True)
    encuesta_id = Column(Integer, ForeignKey("encuestas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Datos personales de quien responde (obligatorios para identificar la participación)
    nombre = Column(String, nullable=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RespuestaItem(Base):
    __tablename__ = "respuesta_items"

    id = Column(Integer, primary_key=True, index=True)
    respuesta_id = Column(Integer, ForeignKey("respuestas_encuesta.id"), nullable=False)
    pregunta_id = Column(Integer, ForeignKey("preguntas.id"), nullable=False)
    valor = Column(String, nullable=True)
