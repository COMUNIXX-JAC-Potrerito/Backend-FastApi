from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.tiempo import ahora_utc
from app.db.session import Base


class PasswordResetToken(Base):
    """Token de un solo uso para restablecer la contraseña.

    Se guarda el *hash* del token (no el token en claro): si se filtra la base,
    los tokens siguen sin servir.
    """

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=ahora_utc)
