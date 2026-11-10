import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.tiempo import ahora_utc
from app.db.session import Base
from app.models.mixins import AdjuntoMixin


def _nuevo_codigo() -> str:
    return uuid.uuid4().hex[:10]


class PQRS(AdjuntoMixin, Base):
    __tablename__ = "pqrs"

    id = Column(Integer, primary_key=True, index=True)
    # Código público para consultar el estado sin iniciar sesión.
    codigo_seguimiento = Column(String, unique=True, index=True, default=_nuevo_codigo)

    tipo = Column(String, nullable=False)  # ver services/pqrs/catalogos.py
    asunto = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(String, nullable=False, default="Nueva")
    es_anonima = Column(Boolean, default=False)

    # Quién la radicó si tenía sesión. Se guarda también en las anónimas para que
    # aparezcan en "Mis PQRS"; la API la oculta a los dignatarios.
    radicado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Contacto (se oculta en la API si la PQRS es anónima).
    nombre_contacto = Column(String, nullable=True)
    email_contacto = Column(String, nullable=True)
    telefono_contacto = Column(String, nullable=True)

    comite = Column(String, nullable=True)  # se asigna después (PUT /pqrs/{id}/asignar)
    # Respuesta única de la versión anterior; las nuevas van en respuestas_pqrs.
    respuesta = Column(String, nullable=True)
    respuesta_fecha = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=ahora_utc)
    updated_at = Column(DateTime, default=ahora_utc, onupdate=ahora_utc)

    respuestas = relationship(
        "RespuestaPQRS",
        back_populates="pqrs",
        order_by="RespuestaPQRS.created_at",
        cascade="all, delete-orphan",
    )


class RespuestaPQRS(Base):
    """Una respuesta de la JAC a una PQRS. Una PQRS puede tener varias."""

    __tablename__ = "respuestas_pqrs"

    id = Column(Integer, primary_key=True, index=True)
    pqrs_id = Column(Integer, ForeignKey("pqrs.id"), nullable=False, index=True)
    autor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    texto = Column(String, nullable=False)

    created_at = Column(DateTime, default=ahora_utc)
    updated_at = Column(DateTime, default=ahora_utc, onupdate=ahora_utc)

    pqrs = relationship("PQRS", back_populates="respuestas")
