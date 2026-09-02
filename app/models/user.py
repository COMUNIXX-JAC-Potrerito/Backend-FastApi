from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)  # celular del usuario
    role = Column(String, nullable=False, default="usuario")  # usuario, administrador, superadministrador, entidad
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
