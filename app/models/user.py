from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.tiempo import ahora_utc
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)  # guardado en minúsculas
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, nullable=False, default="usuario")  # ver services/auth/roles.py
    comite = Column(String, nullable=True)  # comisión/cargo del dignatario
    is_active = Column(Boolean, default=True)  # False bloquea el login y los tokens
    created_at = Column(DateTime, default=ahora_utc)

    @property
    def esta_activo(self) -> bool:
        """Las filas antiguas pueden tener NULL: se consideran activas."""
        return self.is_active is not False
