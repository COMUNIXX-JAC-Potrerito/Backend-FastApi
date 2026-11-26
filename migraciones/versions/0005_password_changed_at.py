"""Marca de tiempo del último cambio de contraseña (invalida JWT anteriores).

Las filas existentes quedan NULL = "nunca cambió": sus tokens vigentes siguen
siendo válidos (ver app/api/deps.py). Al restablecer la contraseña se guarda la
fecha y los tokens emitidos antes dejan de autenticar.

Revisión: 0005
Anterior: 0004
Fecha: 2026-11-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | Sequence[str] | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_changed_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_changed_at")
