import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class PQRS(Base):
    __tablename__ = "pqrs"

    id = Column(Integer, primary_key=True, index=True)

    # Código público para consultar el estado sin iniciar sesión (turistas / anónimas)
    codigo_seguimiento = Column(
        String, unique=True, index=True, default=lambda: uuid.uuid4().hex[:10]
    )

    tipo = Column(String, nullable=False)         # Peticion, Queja, Reclamo, Sugerencia
    asunto = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(String, nullable=False, default="Nueva")  # Nueva, En_Proceso, Finalizada
    es_anonima = Column(Boolean, default=False)

    # Quién la radica SI está logueado (llave foránea a users). Vacío para no registrados.
    radicado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Datos de contacto para no registrados o para notificar (se ocultan si es anónima)
    nombre_contacto = Column(String, nullable=True)
    email_contacto = Column(String, nullable=True)
    telefono_contacto = Column(String, nullable=True)

    comite = Column(String, nullable=True)  # se asigna después (PUT /pqrs/{id}/asignar)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
