from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class EnvioMasivo(Base):
    __tablename__ = "envios_masivos"

    id = Column(Integer, primary_key=True, index=True)
    asunto = Column(String, nullable=False)
    contenido = Column(String, nullable=False)
    destinatarios = Column(Integer, default=0)
    modo = Column(String, nullable=True)  # simulado, real, error
    enviado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
