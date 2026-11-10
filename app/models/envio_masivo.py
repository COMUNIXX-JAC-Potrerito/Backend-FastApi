from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.tiempo import ahora_utc
from app.db.session import Base


class EnvioMasivo(Base):
    __tablename__ = "envios_masivos"

    id = Column(Integer, primary_key=True, index=True)
    asunto = Column(String, nullable=False)
    contenido = Column(String, nullable=False)
    destinatarios = Column(Integer, default=0)
    modo = Column(String, nullable=True)  # simulado | real | parcial | error
    enviado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=ahora_utc)
